import pandas as pd

from src.av_constants import (
    AV_CANDLE_TF,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_SYMBOL,
)
from src.av_integration import AlphaVantageAPIHandler


def main() -> None:
    handler = AlphaVantageAPIHandler(api_key="demo")
    retval = handler.get_historical_options(AV_SYMBOL.IBM)

    print(retval)


if __name__ == "__main__":
    main()
