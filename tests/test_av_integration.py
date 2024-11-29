from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from src.av_integration import (
    AV_CANDLE_TF,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_SYMBOL,
    AlphaVantageAPIHandler,
)
from src.constants import options_columns

handler = AlphaVantageAPIHandler("demo")


def validate_candles(candle_df: pd.DataFrame) -> None:
    """
    Validates the structure and data types of the returned candle data.
    """
    assert isinstance(candle_df, pd.DataFrame)
    assert isinstance(candle_df.index, pd.DatetimeIndex)
    assert all(
        [candle_df[k].dtype == np.float32 for k in ["Open", "High", "Low", "Close"]]
    )
    if "Volume" in candle_df:
        assert candle_df["Volume"].dtype == np.int32


def parallel_validate_candles(av_handler, call_details_list):
    """
    Runs API calls concurrently and validates their results.
    """
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(getattr(av_handler, details["method"]), **details["kwargs"])
            for details in call_details_list
        ]

        for future, details in zip(as_completed(futures), call_details_list):
            try:
                candle_df = future.result()
                validate_candles(candle_df)
                print(f"Validation passed for call: {details}")
            except Exception as e:
                print(f"Validation failed for call: {details} with error: {e}")


def test_get_time_series_parallel() -> None:
    """
    Tests both daily and intraday time series in parallel.
    """
    # fmt: off
    call_details_list = [
        # Daily time series calls
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.IBM}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.IBM, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.TSCO_LON, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.SHOP_TRT, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.GPV_TRV, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.MBG_DEX, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL.RELIANCE_BSE, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL._600104_SHH, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_SYMBOL._000002_SHZ, "outputsize": "full"}},

        # Intraday time series calls
        {"method": "get_time_series_intraday", "kwargs": {"symbol": AV_SYMBOL.IBM, "interval": AV_CANDLE_TF.MIN5}},
        {"method": "get_time_series_intraday", "kwargs": {"symbol": AV_SYMBOL.IBM, "interval": AV_CANDLE_TF.MIN5, "outputsize": "full"}},
    ]
    # fmt: on

    parallel_validate_candles(handler, call_details_list)


def test_get_currency_exchange_pair() -> None:
    bid, ask = handler.get_currency_exchange_pair(
        from_currency=AV_CURRENCY.USD, to_currency=AV_CURRENCY.JPY
    )
    assert isinstance(bid, float)
    assert isinstance(ask, float)
    assert 0.0 < bid < ask

    bid, ask = handler.get_currency_exchange_pair(
        from_currency=AV_CURRENCY_DIGITAL.BTC, to_currency=AV_CURRENCY.EUR
    )
    assert isinstance(bid, float)
    assert isinstance(ask, float)
    assert 0.0 < bid < ask


def test_get_historical_options() -> None:
    df = handler.get_historical_options(AV_SYMBOL.IBM)
    assert set(df.columns) == set(options_columns)

    df = handler.get_historical_options(AV_SYMBOL.IBM, date="2017-11-15")
    assert set(df.columns) == set(options_columns)
