from header import *

# Remove after checking profitability
buy_price: float = 0.0


def get_base_currency_price(symbol: str) -> float:
    """Gets the price of the given currency.
    Only works for currencies in BASE_CURRENCIES."""

    if symbol == "WETH":
        return float(requests.get(WETH_PRICE_URL).json()["weth"]["usd"])
    
    return 1.0

def is_token_safe(pair: Pair, currency: str) -> bool:
    """Checks if the given pair is safe to buy."""
    
    base_currency_price: float = get_base_currency_price(pair.base_currency)
    
    isrug_liq_url: str = gen_isrug_liq_url(currency, pair.token_id)


    liq_data_before: dict = requests.get(isrug_liq_url).json()["liqs"]

    if (
        liq_data_before["name"] != pair.base_currency or
        bool(liq_data_before["emptyLiq"]) or
        bool(liq_data_before["isRugged"])
    ):
        return False

    liq_before_usd: float = float(liq_data_before["rawQuoteLiq"]) \
        * base_currency_price

    if liq_before_usd < MINIMUM_USD_LIQUIDITY:
        return False

    time.sleep(TIME_TO_WAIT_BEFORE_CHECKING_TOKEN_SAFETY)

    # Remove after checking profitability
    global buy_price
    buy_price = float(
        requests.get(
            url = f"https://www.dextools.io/chain-{currency}/api/generic/history/candles/v2?latest=1d&pair={pair.id}&sym=usd",
            headers = HEADERS_DEXTOOLS
        ).json()["data"]["candles"][-1]["close"]
    )

    liq_data_after: dict = requests.get(isrug_liq_url).json()["liqs"]

    if (
        bool(liq_data_after["emptyLiq"]) or
        bool(liq_data_after["isRugged"])
    ):
        return False
    
    liq_after_usd: float = float(liq_data_after["rawQuoteLiq"]) \
        * base_currency_price
    
    if liq_after_usd / liq_before_usd < MINIMUM_LIQUIDITY_MULTIPLIER:
        return False
    
    isrug_basic_scan: dict = requests.get(
        gen_isrug_scan_url(currency, pair.token_id, "basic")
    ).json()["result"]

    if (
        float(isrug_basic_scan["buyTax"]) > MAXIMUM_BUY_TAX or
        float(isrug_basic_scan["sellTax"]) > MAXIMUM_SELL_TAX or
        (not bool(isrug_basic_scan["isSellable"])) or 
        bool(isrug_basic_scan["transferError"])
    ):
        return False
    
    isrug_detailed_scan: str = requests.get(
        gen_isrug_scan_url(currency, pair.token_id, "detailed")
    )

    detailed_scan_json: dict = isrug_detailed_scan.json()
    
    if int(detailed_scan_json["holders"]["totalHolders"]) < MINIMUM_HOLDERS:
        return False

    if (
        "\"isVerified\":true," in isrug_detailed_scan and
        f"\"owner\":\"{NULL_ADDRESS}\"" in isrug_detailed_scan and
        "\"renounced\":true" in isrug_detailed_scan and
        "\"knownScammer\":false" in isrug_detailed_scan and
        "\"hiddenMint\":false" in isrug_detailed_scan and
        "\"withBalance\":false," in isrug_detailed_scan and
        "\"withUnknown\":false" in isrug_detailed_scan
    ):
        return True
    
    return False

def compute_token(pair: Pair, currency: str, filename: str) -> None:
    """Checks if the given pair is safe to buy,
    and if so, buys it then sells it.
    Logs the profit and loss to a file."""

    try:
        if not is_token_safe(pair, currency):
            return
    except:
        return
    
    time.sleep(TIME_TO_WAIT_BEFORE_SELLING)


    ### Quick and dirty code to log the profit and loss to a file, re-factor after checking profitablity ###

    profit = 0.0

    try:
        isrug_basic_scan: dict = requests.get(
            gen_isrug_scan_url(currency, pair.token_id, "basic")
        ).json()["result"]

        sell_tax: float = float(isrug_basic_scan["sellTax"])

        if not bool(isrug_basic_scan["isSellable"]):
            raise Exception()
        
        sell_price: float = float(
            requests.get(
                url = f"https://www.dextools.io/chain-{currency}/api/generic/history/candles/v2?latest=1d&pair={pair.id}&sym=usd",
                headers = HEADERS_DEXTOOLS
            ).json()["data"]["candles"][-1]["close"]
        )

        profit = (sell_price / buy_price) * (1 - sell_tax / 100)
    except:
        profit = 0.0

    # a file append should be atomic on most systems, so there is no need to lock the file for this test
    os.system(f"echo {profit} >> {filename}")
