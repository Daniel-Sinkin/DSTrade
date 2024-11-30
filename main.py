import os

import pandas as pd
from dotenv import load_dotenv

from src.av_integration import AlphaVantageHandler
from src.av_util import AV_CURRENCY, AV_CURRENCY_DIGITAL

load_dotenv()
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")
if API_KEY_ALPHAVANTAGE is None:
    raise RuntimeError(
        "Couldn't find the Alphavantage api key in the environment variables!"
    )


def main() -> None:
    handler = AlphaVantageHandler(API_KEY_ALPHAVANTAGE)
    print("STOCK:")
    print()
    print(handler.get_candles(ctf="1day", symbol="IBM"))
    print()

    print()
    print("FOREX:")
    print()
    print(
        handler.get_candles(
            ctf="1day", from_symbol=AV_CURRENCY.EUR, to_symbol=AV_CURRENCY.USD
        )
    )


if __name__ == "__main__":
    main()
