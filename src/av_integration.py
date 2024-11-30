import logging
from typing import Literal, Optional, cast, overload

import numpy as np
import pandas as pd

from .av_integration_api import AlphaVantageAPIHandler
from .av_util import (
    AV_CANDLE_TF,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_DATA_CANDLE,
    AV_SYMBOL,
    obfuscate_api_key,
)

handler_logger = logging.Logger("AV_APIHandler")
handler_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

handler_logger.addHandler(stream_handler)


class AlphaVantageHandler:
    def __init__(self, api_key: str = "demo"):
        self._api = AlphaVantageAPIHandler(api_key=api_key)
        self.logger = handler_logger
        self.logger.debug(f"Created {self}.")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"AlphaVantageHandler(api_key={obfuscate_api_key(self._api.api_key)})"

    # fmt: off
    @overload
    def get_candles(self, ctf: AV_CANDLE_TF, symbol: AV_SYMBOL, month: Optional[str] = None, outputsize: Literal["full", "compact"] = "full") -> Optional[pd.DataFrame]: ...
    @overload
    def get_candles(self, ctf: AV_CANDLE_TF, currency_from: AV_CURRENCY, currency_to: AV_CURRENCY, outputsize: Literal["full", "compact"] = "full") -> Optional[pd.DataFrame]: ...
    @overload
    def get_candles(self, ctf: AV_CANDLE_TF, crypto: AV_CURRENCY_DIGITAL, currency: AV_CURRENCY, outputsize: Literal["full", "compact"] = "full") -> Optional[pd.DataFrame]: ...
    # fmt: on
    def get_candles(
        self,
        ctf: AV_CANDLE_TF,
        outputsize: Literal["full", "compact"] = "full",
        **kwargs,
    ) -> Optional[pd.DataFrame]:
        """Note: We discard the volumes from the data."""
        if "symbol" in kwargs:
            symbol = kwargs["symbol"]
            if ctf == AV_CANDLE_TF.MONTHLY:
                data = self._api.get_time_series_monthly(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Monthly Time Series"])
            elif ctf == AV_CANDLE_TF.WEEKLY:
                data = self._api.get_time_series_weekly(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Weekly Time Series"])
            elif ctf == AV_CANDLE_TF.DAY:
                data = self._api.get_time_series_daily(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Time Series (Daily)"])
            else:
                data = self._api.get_time_series_intraday(
                    symbol=symbol,
                    interval=ctf,
                    month=kwargs.get("month"),
                    outputsize="full",
                    **kwargs,
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data[f"Time Series ({ctf})"])
        elif "currency_from" in kwargs and "currency_to" in kwargs:
            from_symbol = kwargs["currency_from"]
            to_symbol = kwargs["currency_to"]
            if ctf == AV_CANDLE_TF.MONTHLY:
                data = self._api.get_fx_monthly(
                    from_symbol=from_symbol,
                    to_symbol=to_symbol,
                    outputsize="full",
                    **kwargs,
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Time Series FX (Monthly)"])
            elif ctf == AV_CANDLE_TF.WEEKLY:
                data = self._api.get_fx_weekly(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Weekly Time Series (Weekly)"])
            elif ctf == AV_CANDLE_TF.DAY:
                data = self._api.get_fx_daily(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data["Time Series (Daily)"])
            else:
                data = self._api.get_fx_intraday(
                    from_symbol=from_symbol,
                    to_symbol=to_symbol,
                    interval=ctf,
                    month=kwargs.get("month"),
                    outputsize="full",
                    **kwargs,
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data[f"Time Series ({ctf})"])
        elif "crypto" in kwargs and "currency" in kwargs:
            symbol = kwargs["crypto"]
            market = kwargs["currency"]
            if ctf == AV_CANDLE_TF.MONTHLY:
                data = self._api.get_digital_currency_monthly(
                    symbol=symbol,
                    market=market,
                    outputsize="full",
                    **kwargs,
                )
                if data is None:
                    return None
                candle_data = cast(
                    AV_DATA_CANDLE, data["Time Series (Digital Currency Monthly)"]
                )
            elif ctf == AV_CANDLE_TF.WEEKLY:
                data = self._api.get_digital_currency_weekly(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(
                    AV_DATA_CANDLE, data["Time Series (Digital Currency Weekly)"]
                )
            elif ctf == AV_CANDLE_TF.DAY:
                data = self._api.get_digital_currency_daily(
                    symbol=symbol, outputsize="full", **kwargs
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data[f"Time Series Crypto ({ctf})"])
            else:
                data = self._api.get_crypto_intraday(
                    from_symbol=from_symbol,
                    to_symbol=to_symbol,
                    interval=ctf,
                    month=kwargs.get("month"),
                    outputsize="full",
                    **kwargs,
                )
                if data is None:
                    return None
                candle_data = cast(AV_DATA_CANDLE, data[f"Time Series ({ctf})"])
        else:
            raise ValueError(f"{kwargs=} is not supported for a get_candles call.")

        self.logger.debug("get_candles meta data: %s", data["Meta Data"])

        df = pd.DataFrame.from_dict(candle_data, orient="index")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

        df.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
            },
            inplace=True,
        )
        df = df.astype(
            {
                "Open": np.float32,
                "High": np.float32,
                "Low": np.float32,
                "Close": np.float32,
            }
        )
        if "symbol" in kwargs:
            self.logger.debug("Pulled %d daily candles for %s", len(df), symbol)
        else:
            self.logger.debug(
                "Pulled %d daily candles for %s/%s", len(df), from_symbol, to_symbol
            )
        return df
