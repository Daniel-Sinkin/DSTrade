import numpy as np
import pandas as pd

from src.av_integration import AlphaVantageHandler
from src.av_util import AV_CANDLE_TF

handler = AlphaVantageHandler(api_key="demo")


def validate_candles(candles) -> None:
    assert isinstance(
        candles,
        pd.DataFrame,
    )
    assert set(candles.columns) == {"Open", "High", "Low", "Close", "Volume"}

    assert candles["Open"].dtype == np.float32
    assert candles["High"].dtype == np.float32
    assert candles["Low"].dtype == np.float32
    assert candles["Close"].dtype == np.float32
    assert candles["Volume"].dtype == np.int32

    assert isinstance(candles.index, pd.DatetimeIndex)

    bad_candles = 0
    bad_candles += (candles["Low"] > candles["Open"]).sum()
    bad_candles += (candles["Open"] > candles["High"]).all()
    bad_candles += (candles["Low"] > candles["Close"]).all()
    bad_candles += (candles["Close"] > candles["High"]).all()
    assert bad_candles < 0.05 * len(candles)  # Give some slack for mispriced candles


def test_get_candles() -> None:
    candles_stock = handler.get_candles(ctf=AV_CANDLE_TF.DAY, symbol="IBM")
    validate_candles(candles_stock)

    candles_fx = handler.get_candles(
        ctf=AV_CANDLE_TF.DAY, from_symbol="EUR", to_symbol="USD"
    )
    validate_candles(candles_fx)
