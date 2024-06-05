#!/usr/bin/env python3

from header import *
from compute_token import compute_token

if __name__ == "__main__":

    currency: str = sys.argv[1] if len(sys.argv) > 1 else ""
    
    csv_file: str = f"{currency}-{os.getpid()}.csv"

    if currency not in VALID_CURRENCIES:
        print(USAGE)
        sys.exit(1)

    dry_run: bool = True if len(sys.argv) > 2 and \
        sys.argv[2] == DRY_RUN_FLAG else False

    if not dry_run:
        print(REAL_RUN_MESSAGE)
        sys.exit(1)
    else:
        print(DRY_RUN_MESSAGE)

    print(f"Starting {NAME} for {currency}...\n\nPess ENTER to quit.")

    dextools_url: str = gen_dextools_url(currency)

    lastest_pairs_old: list[Pair | None] = [None] * PAIRS_TO_KEEP

    # while enter not pressed.
    # This abomination is needed to make the stdin read non-blocking.
    while not select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        time.sleep(SLEEP_TIME_REQUESTS)
        try:
            request_json: dict = requests.get(
                url = dextools_url,
                headers = HEADERS_DEXTOOLS
            ).json()

            if request_json["code"] != "OK":
                raise Exception()

            latest_pairs: list[Pair | None] = [Pair(create) for create in \
                request_json["data"]["creates"][:5]]

            # for every pair in latest_pairs that is not in lastest_pairs_old
            for pair in [
                    pair for pair in latest_pairs
                    if pair is not None
                    and pair.id not in [
                        pair.id for pair in lastest_pairs_old
                        if pair is not None
                    ]
                ]:
                # start a new process to compute the token in the background
                multiprocessing.Process(
                    target = compute_token,
                    args = (pair, currency, csv_file)
                ).start()

            lastest_pairs_old = latest_pairs

        except:
            print("Error fetching data from dextools, retrying...")
            continue

    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
