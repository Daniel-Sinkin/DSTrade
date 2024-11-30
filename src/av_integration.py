import logging
from typing import Literal, Optional, cast, overload

import numpy as np
import pandas as pd

from .av_integration_api import AlphaVantageAPIHandler
from .av_util import (
    AV_CANDLE_TF,
    AV_CANDLE_TYPE,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_DATA_CANDLE,
    AV_SYMBOL,
    obfuscate_api_key,
)

handler_logger = logging.Logger("AV_Handler")
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

    @staticmethod
    def _candle_data_to_df(
        candle_data: list[AV_DATA_CANDLE], ohlc_fmt: list[str] = None
    ) -> pd.DataFrame:
        if len(candle_data) == 0:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close"])
        if ohlc_fmt is None:
            ohlc_fmt = ["1. open", "2. high", "3. low", "4. close"]
        df = cast(pd.DataFrame, pd.DataFrame.from_dict(candle_data, orient="index"))
        if "5. volume" in df:
            df.drop(columns="5. volume", inplace=True)
        df.index = pd.to_datetime(df.index, format="mixed")

        renamer_map = {
            old: new for old, new in zip(ohlc_fmt, ["Open", "High", "Low", "Close"])
        }
        df.rename(
            columns=renamer_map,
            inplace=True,
        )
        df = df.astype(np.float32)

        return df

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
        ctf: AV_CANDLE_TF | str,
        outputsize: Literal["full", "compact"] = "full",
        **kwargs,
    ):
        """Note: We discard the volumes from the data."""
        if isinstance(ctf, str):
            ctf = AV_CANDLE_TF(ctf)
        if "symbol" in kwargs:
            candle_type = AV_CANDLE_TYPE.STOCK
            symbol = cast(AV_SYMBOL, kwargs.pop("symbol"))
            candle_data = self.get_candles_stocks(
                ctf=ctf, symbol=symbol, outputsize=outputsize, **kwargs
            )
        elif "currency_from" in kwargs and "currency_to" in kwargs:
            candle_type = AV_CANDLE_TYPE.FOREX
            from_symbol = cast(AV_CURRENCY, kwargs.pop("currency_from"))
            to_symbol = cast(AV_CURRENCY, kwargs.pop("currency_to"))
            candle_data = self.get_candles_forex(
                ctf=ctf,
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                outputsize=outputsize,
                **kwargs,
            )
        elif "crypto" in kwargs and "currency" in kwargs:
            candle_type = AV_CANDLE_TYPE.CRYPTO
            symbol = cast(AV_CURRENCY_DIGITAL, kwargs.pop("crypto"))
            market = cast(AV_CURRENCY, kwargs.pop("currency"))
            candle_data = self.get_candles_crypto(
                ctf=ctf, symbol=symbol, market=market, outputsize=outputsize, **kwargs
            )
        else:
            raise ValueError(f"{kwargs=} is not supported for a get_candles call.")

        if candle_data is None:
            return None

        candle_data = cast(list[AV_DATA_CANDLE], candle_data)
        match candle_type:
            case AV_CANDLE_TYPE.STOCK:
                self.logger.debug(
                    "Pulled %d %s candles for %s.", len(candle_data), ctf, symbol
                )
            case AV_CANDLE_TYPE.FOREX:
                self.logger.debug(
                    "Pulled %d %s forex candles for %s/%s.",
                    len(candle_data),
                    ctf,
                    from_symbol,
                    to_symbol,
                )
            case AV_CANDLE_TYPE.CRYPTO:
                self.logger.debug(
                    "Pulled %d %s crypto candles for %s (in %s).",
                    len(candle_data),
                    ctf,
                    symbol,
                    market,
                )
        df = AlphaVantageHandler._candle_data_to_df(candle_data)
        return df

    def get_candles_stocks(
        self,
        ctf: AV_CANDLE_TF,
        symbol: AV_SYMBOL,
        outputsize: Literal["full", "compact"] = "full",
        **kwargs,
    ) -> Optional[list[AV_DATA_CANDLE]]:
        if ctf == AV_CANDLE_TF.MONTH:
            data = self._api.get_time_series_monthly(symbol=symbol, **kwargs)
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Monthly Time Series"])
        elif ctf == AV_CANDLE_TF.WEEK:
            data = self._api.get_time_series_weekly(symbol=symbol, **kwargs)
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Weekly Time Series"])
        elif ctf == AV_CANDLE_TF.DAY:
            data = self._api.get_time_series_daily(
                symbol=symbol, outputsize=outputsize, **kwargs
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Time Series (Daily)"])
        else:
            data = self._api.get_time_series_intraday(
                symbol=symbol,
                interval=ctf,
                month=kwargs.pop("month"),
                outputsize=outputsize,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data[f"Time Series ({ctf})"])
        return candle_data

    def get_candles_forex(
        self,
        ctf: AV_CANDLE_TF,
        from_symbol: AV_SYMBOL,
        to_symbol: AV_CURRENCY,
        outputsize: Literal["full", "compact"] = "full",
        **kwargs,
    ) -> Optional[list[AV_DATA_CANDLE]]:
        if ctf == AV_CANDLE_TF.MONTH:
            data = self._api.get_fx_monthly(
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Time Series FX (Monthly)"])
        elif ctf == AV_CANDLE_TF.WEEK:
            data = self._api.get_fx_weekly(
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Time Series FX (Weekly)"])
        elif ctf == AV_CANDLE_TF.DAY:
            data = self._api.get_fx_daily(
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                outputsize=outputsize,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data["Time Series FX (Daily)"])
        else:
            data = self._api.get_fx_intraday(
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                interval=ctf,
                outputsize=outputsize,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data[f"Time Series FX ({ctf})"])
        return candle_data

    def get_candles_crypto(
        self,
        ctf: AV_CANDLE_TF,
        symbol: AV_CURRENCY_DIGITAL,
        market: AV_CURRENCY,
        outputsize: Literal["full", "compact"] = "full",
        **kwargs,
    ) -> Optional[list[AV_DATA_CANDLE]]:
        if ctf == AV_CANDLE_TF.MONTH:
            data = self._api.get_digital_currency_monthly(
                symbol=symbol,
                market=market,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(
                AV_DATA_CANDLE, data["Time Series (Digital Currency Monthly)"]
            )
        elif ctf == AV_CANDLE_TF.WEEK:
            data = self._api.get_digital_currency_weekly(
                symbol=symbol,
                market=market,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(
                AV_DATA_CANDLE, data["Time Series (Digital Currency Weekly)"]
            )
        elif ctf == AV_CANDLE_TF.DAY:
            data = self._api.get_digital_currency_daily(
                symbol=symbol,
                market=market,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(
                AV_DATA_CANDLE, data["Time Series (Digital Currency Daily)"]
            )
        else:
            data = self._api.get_crypto_intraday(
                symbol=symbol,
                market=market,
                interval=ctf,
                outputsize=outputsize,
                **kwargs,
            )
            if data is None:
                return None
            candle_data = cast(AV_DATA_CANDLE, data[f"Time Series Crypto ({ctf})"])
        return candle_data
