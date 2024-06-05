import os
import sys
import time
import select
import termios
import requests
import fake_useragent
import multiprocessing


### USER CONFIGURABLE VARIABLES ###

MINIMUM_USD_LIQUIDITY: float = 10_000.0
"""Minimum USD liquidity to buy the token. USD price is
calculated from the current price of the base currency."""

TIME_TO_WAIT_BEFORE_CHECKING_TOKEN_SAFETY: int = 60 # 1 minute
"""Time to sleep before checking if the token is safe to buy."""

MINIMUM_LIQUIDITY_MULTIPLIER: float = 1.01
"""Minimum liquidity multiplier after waiting to buy the token."""

TIME_TO_WAIT_BEFORE_SELLING: int = 7 * 60 # 7 minutes
"""Time to sleep before selling the token."""

MAXIMUM_BUY_TAX: float = 5.0
"""Maximum buy tax in percentage."""

MAXIMUM_SELL_TAX: float = 5.0
"""Maximum sell tax in percentage."""

MINIMUM_HOLDERS: int = 10
"""Minimum number of holders."""

### END USER CONFIGURABLE VARIABLES ###


class Pair:
    id: str
    token_id: str
    base_currency: str

    def __init__(self, pair_json: dict) -> None:
        self.id = pair_json["id"]

        self.base_currency = pair_json["token0"]["symbol"]

        if self.base_currency not in BASE_CURRENCIES:
            self.base_currency = pair_json["token1"]["symbol"]

        if self.base_currency not in BASE_CURRENCIES:
            raise Exception()

        if pair_json["token0"]["symbol"] != self.base_currency:
            self.token_id = pair_json["token0"]["id"]
        else:
            self.token_id = pair_json["token1"]["id"]
        
        if self.token_id == "":
            raise Exception()

NAME: str = "defi-autopilot"
"""Name of the program."""

VALID_CURRENCIES: list[str] = [
    "ethereum",
    "arbitrum"
]
"""List of valid currency names"""

DRY_RUN_FLAG: str = "dry-run"
"""Flag to enable dry-run mode."""

USAGE: str = (
    "Usage: {} <currency> [{}]\n\n"
    "The currency must be one of the following:\n"
    "{}\n"
).format(
    NAME,
    DRY_RUN_FLAG,
    "\n".join([f"  - {currency}" for currency in VALID_CURRENCIES])
)
"""Usage string."""

DRY_RUN_MESSAGE: str = "Dry run selected, no transactions will be made.\n"
"""Message to print when dry-run is selected."""

REAL_RUN_MESSAGE: str = "Real run not implemented yet, " \
    "please run in dry-run mode. exiting..."
"""Message to print when real-run is selected."""


DEXTOOLS_BASE_URL: str = "https://www.dextools.io"
"""Base url for dextools."""

ISRUG_BASE_URL: str = "https://isrug.app"

HEADERS_DEXTOOLS: dict[str, str] = {
    "referer": DEXTOOLS_BASE_URL,
    "User-Agent": fake_useragent.UserAgent().chrome
}
"""Headers for dextools pool-explorer requests."""

SLEEP_TIME_REQUESTS: int = 5
"""Time to sleep between requests to dextools."""

PAIRS_TO_KEEP: int = 5
"""Number of pairs to keep track of in case many pairs are created at once."""

BASE_CURRENCIES: list[str] = [
    "WETH",
    "USDT",
    "USDC"
]
"""List of base currencies."""

WETH_PRICE_URL: str = "https://api.coingecko.com" \
    "/api/v3/simple/price?ids=weth&vs_currencies=usd"
"""URL to get the current WETH price."""

NULL_ADDRESS: str = "0x0000000000000000000000000000000000000000"
"""Null ethereum address."""

def gen_dextools_url(currency: str) -> str:
    """Generates the dextools pool-explorer url for the given currency."""

    return f"{DEXTOOLS_BASE_URL}/chain-{currency}/api/generic/pools"

def gen_isrug_liq_url(currency: str, token: str) -> str:
    """Generates the isrug.app liquidity url
    with the given currency and token."""

    return f"{ISRUG_BASE_URL}/tokens/liq?chain={currency}&addr={token}"

def gen_isrug_scan_url(currency: str, token: str, mode: str) -> str:
    """Generates the isrug.app scan url
    with the given currency, token and mode."""

    return f"{ISRUG_BASE_URL}/tokens/scan" \
        "?mode={mode}&chain={currency}&addr={token}"
