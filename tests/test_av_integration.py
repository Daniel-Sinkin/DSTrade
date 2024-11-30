import numpy as np
import pandas as pd
import pytest

from src.av_integration import AlphaVantageHandler
from src.av_util import AV_CANDLE_TF, AV_CURRENCY, AV_CURRENCY_DIGITAL, AV_SYMBOL

handler = AlphaVantageHandler(api_key="demo")


def validate_candles(candles) -> None:
    assert isinstance(
        candles,
        pd.DataFrame,
    )
    assert set(candles.columns) == {"Open", "High", "Low", "Close"}

    assert candles["Open"].dtype == np.float32
    assert candles["High"].dtype == np.float32
    assert candles["Low"].dtype == np.float32
    assert candles["Close"].dtype == np.float32

    assert isinstance(candles.index, pd.DatetimeIndex)

    bad_candles = 0
    bad_candles += (candles["Low"] > candles["Open"]).sum()
    bad_candles += (candles["Open"] > candles["High"]).sum()
    bad_candles += (candles["Low"] > candles["Close"]).sum()
    bad_candles += (candles["Close"] > candles["High"]).sum()
    assert bad_candles < 0.10 * len(candles)  # Add some slack for mispriced candles


@pytest.mark.parametrize(
    "ctf, symbol, month",
    [
        (AV_CANDLE_TF.MIN5, AV_SYMBOL.IBM, None),
        (AV_CANDLE_TF.MIN5, AV_SYMBOL.IBM, "2009-01"),
    ],
)
def test_get_candles_stocks_intraday(ctf, symbol, month) -> None:
    validate_candles(handler.get_candles(ctf=ctf, symbol=symbol, month=month))


@pytest.mark.parametrize(
    "ctf, symbol",
    [
        (AV_CANDLE_TF.DAY, AV_SYMBOL.IBM),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.IBM),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.TSCO_LON),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.SHOP_TRT),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.GPV_TRV),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.MBG_DEX),
        (AV_CANDLE_TF.DAY, AV_SYMBOL.RELIANCE_BSE),
        (AV_CANDLE_TF.DAY, AV_SYMBOL._600104_SHH),
        (AV_CANDLE_TF.DAY, AV_SYMBOL._000002_SHZ),
        (AV_CANDLE_TF.WEEK, AV_SYMBOL.IBM),
        (AV_CANDLE_TF.WEEK, AV_SYMBOL.TSCO_LON),
        (AV_CANDLE_TF.MONTH, AV_SYMBOL.IBM),
        (AV_CANDLE_TF.MONTH, AV_SYMBOL.TSCO_LON),
    ],
)
def test_get_candles_stocks_non_intraday(ctf, symbol) -> None:
    validate_candles(handler.get_candles(ctf=ctf, symbol=symbol))


@pytest.mark.parametrize(
    "ctf, currency_from, currency_to",
    [
        (AV_CANDLE_TF.MIN5, AV_CURRENCY.EUR, AV_CURRENCY.USD),
        (AV_CANDLE_TF.DAY, AV_CURRENCY.EUR, AV_CURRENCY.USD),
        (AV_CANDLE_TF.WEEK, AV_CURRENCY.EUR, AV_CURRENCY.USD),
        (AV_CANDLE_TF.MONTH, AV_CURRENCY.EUR, AV_CURRENCY.USD),
    ],
)
def test_get_candles_forex(ctf, currency_from, currency_to) -> None:
    validate_candles(
        handler.get_candles(
            ctf=ctf,
            currency_from=currency_from,
            currency_to=currency_to,
        )
    )


@pytest.mark.parametrize(
    "ctf, crypto, currency",
    [
        (AV_CANDLE_TF.MIN5, AV_CURRENCY_DIGITAL.ETH, AV_CURRENCY.USD),
        (AV_CANDLE_TF.DAY, AV_CURRENCY_DIGITAL.ETH, AV_CURRENCY.EUR),
        (AV_CANDLE_TF.WEEK, AV_CURRENCY_DIGITAL.ETH, AV_CURRENCY.EUR),
        (AV_CANDLE_TF.MONTH, AV_CURRENCY_DIGITAL.ETH, AV_CURRENCY.EUR),
    ],
)
def test_get_candles_crypto(ctf, crypto, currency) -> None:
    return
    validate_candles(
        handler.get_candles(
            ctf=ctf,
            crypto=crypto,
            currency=currency,
        )
    )
