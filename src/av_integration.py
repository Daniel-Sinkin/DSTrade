import logging
from typing import Optional

import numpy as np
import pandas as pd

from .av_integration_api import AlphaVantageAPIHandler
from .av_util import AV_CANDLE_TF, AV_SYMBOL, obfuscate_api_key

handler_logger = logging.Logger("AV_APIHandler")
handler_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

handler_logger.addHandler(stream_handler)


class AlphaVantageHandler:
    def __init__(self, api_key: str):
        self._api = AlphaVantageAPIHandler(api_key=api_key)
        self.logger = handler_logger
        self.logger.debug(f"Created {self}.")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"AlphaVantageHandler(api_key={obfuscate_api_key(self.api_key)})"

    def get_candles(self, ctf: AV_CANDLE_TF, **symbol_kwargs) -> Optional[pd.DataFrame]:
        """
        symbol_kwargs either contains "symbol" then we are dealing with stock candles
        or it contains "from_symbol" and "to_symbol" and we are dealing with a Forex Pair.
        """
        if "symbol" in symbol_kwargs:
            symbol = symbol_kwargs["symbol"]
            if ctf == AV_CANDLE_TF.DAY:
                data = self._api.get_time_series_daily(symbol=symbol, outputsize="full")
                if data is None:
                    return None
                candle_data = data["Time Series (Daily)"]
            else:
                raise NotImplementedError("intraday Candles are not supported yet.")
        else:
            assert "from_symbol" in symbol_kwargs and "to_symbol" in symbol_kwargs
            from_symbol = symbol_kwargs["from_symbol"]
            to_symbol = symbol_kwargs["to_symbol"]
            if ctf == AV_CANDLE_TF.DAY:
                data = self._api.get_fx_daily(
                    from_symbol=from_symbol, to_symbol=to_symbol, outputsize="full"
                )
                if data is None:
                    return None
                candle_data = data["Time Series FX (Daily)"]
            else:
                raise NotImplementedError("intraday Candles are not supported yet.")

        self.logger.debug("get_candles meta data: %s", data["Meta Data"])

        df = pd.DataFrame.from_dict(candle_data, orient="index")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

        df.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            },
            inplace=True,
        )
        if "Volume" not in df:
            df["Volume"] = 0  # Forex has no volume
        df = df.astype(
            {
                "Open": np.float32,
                "High": np.float32,
                "Low": np.float32,
                "Close": np.float32,
                "Volume": np.int32,
            }
        )
        if "symbol" in symbol_kwargs:
            self.logger.debug("Pulled %d daily candles for %s", len(df), symbol)
        else:
            self.logger.debug(
                "Pulled %d daily candles for %s/%s", len(df), from_symbol, to_symbol
            )
        return df
