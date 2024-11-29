import os

import pandas as pd
from dotenv import load_dotenv

from src.av_integration import AlphaVantageAPIHandler

load_dotenv()
av_api_key = os.getenv("API_KEY_ALPHAVANTAGE")
if av_api_key is None:
    raise RuntimeError("AV API key couldn't be found in the environment variables.")


def main() -> None:
    handler = AlphaVantageAPIHandler(av_api_key)

    handler.get_time_series_daily


if __name__ == "__main__":
    main()
