import datetime as dt
import os

import matplotlib.pyplot as plt
import numpy as np
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

    months = list(range(1, 10))
    months_fmt = [f"2024-{month:02}" for month in months]
    print(months_fmt)

    months2 = list(range(1, 12))
    months2_fmt = [f"2023-{month:02}" for month in months2]

    for month in months_fmt:
        df: pd.DataFrame = handler.get_candles(ctf="1min", symbol="IBM", month=month)
        df.to_pickle(f"{month}.pkl")

    for month in months2_fmt:
        df: pd.DataFrame = handler.get_candles(ctf="1min", symbol="IBM", month=month)
        df.to_pickle(f"2023-{month}.pkl")


if __name__ == "__main__":
    main()
