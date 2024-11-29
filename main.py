import pandas as pd

from src.av_constants import (
    AV_CANDLE_TF,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_SYMBOL,
)
from src.av_integration_old import AlphaVantageAPIHandler


def main() -> None:
    handler = AlphaVantageAPIHandler(api_key="demo")
    retval = handler.get_sentiment(tickers=[AV_SYMBOL.AAPL])

    print(retval)


if __name__ == "__main__":
    main()
