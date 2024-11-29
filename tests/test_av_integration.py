from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from src.av_integration import AV_CANDLE_TF, AV_TICKER, AlphaVantageAPIHandler

av_handler = AlphaVantageAPIHandler("demo")


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
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.IBM}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.IBM, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.TSCO_LON, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.SHOP_TRT, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.GPV_TRV, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.MBG_DEX, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER.RELIANCE_BSE, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER._600104_SHH, "outputsize": "full"}},
        {"method": "get_time_series_daily", "kwargs": {"symbol": AV_TICKER._000002_SHZ, "outputsize": "full"}},

        # Intraday time series calls
        {"method": "get_time_series_intraday", "kwargs": {"symbol": AV_TICKER.IBM, "interval": AV_CANDLE_TF.MIN5}},
        {"method": "get_time_series_intraday", "kwargs": {"symbol": AV_TICKER.IBM, "interval": AV_CANDLE_TF.MIN5, "outputsize": "full"}},
    ]
    # fmt: on

    parallel_validate_candles(av_handler, call_details_list)
