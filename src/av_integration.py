import datetime as dt
import json
import logging
import os
from typing import Literal, Optional

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

from .av_constants import (
    AV_CANDLE_TF,
    AV_CURRENCY,
    AV_CURRENCY_DIGITAL,
    AV_SYMBOL,
)
from .constants import options_columns

api_logger = logging.Logger("APIHandler")
api_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

api_logger.addHandler(stream_handler)

load_dotenv()
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")
if API_KEY_ALPHAVANTAGE is None:
    raise RuntimeError(
        "Couldn't find the Alphavantage api key in the environment variables!"
    )


def obfuscate_api_key(api_key: str) -> str:
    if api_key == "demo":  # Don't have to obfuscate demo account
        return api_key

    return api_key[:2] + "..." + api_key[-2:]


def obfuscate_request_url(request_url: str, api_key: str) -> str:
    first_part = request_url.split("&apikey=")[0]
    return first_part + f"&apikey={obfuscate_api_key(api_key)}"


def get_utc_timestamp_ms() -> int:
    return int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1000)


class AlphaVantageAPIHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url_base = "https://www.alphavantage.co/"
        self.url_request = self.url_base + "query?"

        self.logger = api_logger

        self.logger.debug(f"Created {self}")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"AlphaVantageAPIHandler(api_key={obfuscate_api_key(self.api_key)})"

    def get_time_series_daily(
        self,
        symbol: AV_SYMBOL | str,
        outputsize: Literal["full", "compact"] = "compact",
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[pd.DataFrame]:
        function = "TIME_SERIES_DAILY"
        data_key = "Time Series (Daily)"

        data = self.send_request(
            function=function,
            request_args=[f"symbol={symbol}"]
            + ([f"outputsize={outputsize}"] if outputsize != "compact" else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            data_key=data_key,
            **kwargs,
        )
        if data is None:
            return None
        df = pd.DataFrame.from_dict(data, orient="index")
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
        df = df.astype(
            {
                "Open": np.float32,
                "High": np.float32,
                "Low": np.float32,
                "Close": np.float32,
                "Volume": np.int32,
            }
        )
        self.logger.debug("Pulled %d daily candles for %s", len(df), symbol)
        return df

    def get_time_series_intraday(
        self,
        symbol: AV_SYMBOL,
        interval: AV_CANDLE_TF,
        adjusted: bool = True,
        extended_hours: bool = True,
        month: Optional[str] = None,
        outputsize: Literal["compact", "full"] = "compact",
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> pd.DataFrame:
        function = "TIME_SERIES_INTRADAY"
        data_key = (f"Time Series ({interval})",)

        data = self.send_request(
            function=function,
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"adjusted={adjusted}",
                f"extended_hours={extended_hours}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"outputsize={outputsize}"] if outputsize != "compact" else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            data_key=data_key,
            **kwargs,
        )
        if data is None:
            return None
        df = pd.DataFrame.from_dict(data, orient="index")
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
        df = df.astype(
            {
                "Open": np.float32,
                "High": np.float32,
                "Low": np.float32,
                "Close": np.float32,
                "Volume": np.int32,
            }
        )
        self.logger.debug("Pulled %d daily candles for %s", len(df), symbol)
        return df

    def get_currency_exchange_pair(
        self,
        from_currency: AV_CURRENCY | AV_CURRENCY_DIGITAL | str,
        to_currency: AV_CURRENCY | AV_CURRENCY_DIGITAL | str,
        **kwargs,
    ) -> tuple[float, float]:
        function = "CURRENCY_EXCHANGE_RATE"
        data_key = "Realtime Currency Exchange Rate"
        from_currency = str(from_currency)
        to_currency = str(to_currency)

        data = self.send_request(
            function=function,
            request_args=[
                f"from_currency={from_currency}",
                f"to_currency={to_currency}",
            ],
            data_key=data_key,
            **kwargs,
        )
        if data is None:
            return None

        bid = float(data["8. Bid Price"])
        ask = float(data["9. Ask Price"])
        return bid, ask

    def get_historical_options(
        self,
        symbol: AV_SYMBOL,
        date: Optional[str] = None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[pd.DataFrame]:
        function = "HISTORICAL_OPTIONS"
        data_key = "data"

        data = self.send_request(
            function=function,
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"date={date}"] if date is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            data_key=data_key,
            **kwargs,
        )
        if data is None:
            return None

        df = pd.DataFrame.from_records(data)
        df.set_index("contractID", inplace=True)
        df.drop(columns="symbol", inplace=True)

        df["expiration"] = pd.to_datetime(df["expiration"])
        df["date"] = pd.to_datetime(df["date"])

        # fmt: off
        float_cols = ["strike", "last", "mark", "bid", "ask", "implied_volatility", "delta", "gamma", "theta", "vega", "rho"]
        int_cols = ["bid_size", "ask_size", "volume", "open_interest"]
        # fmt: on
        for col in float_cols:
            df[col] = df[col].astype(np.float32)

        for col in int_cols:
            df[col] = df[col].astype(np.int32)

        df["is_call"] = np.where(df["type"] == "call", True, False)
        df.drop(columns="type", inplace=True)

        df = df[options_columns]
        return df

    def send_request(
        self,
        function: str,
        request_args: list[str],
        data_key: Optional[str] = None,
        save_result: bool = False,
    ) -> Optional[dict[str, any]]:
        """
        The key where the data is, is rather inconsitent in the API, if data_key
        is not set then we first check if there is only one key, then that one has to be
        the data key, otherwise we check for a list of known non-data keys and return the
        other keys' value (not guaranteed to be correct until everything is implemented)

        Best practice is to just pass it.
        """
        if 'datatype="csv"' in request_args:
            raise NotImplementedError("Currently only JSON is supported!")

        request_url = self.url_request + "&".join(
            [f"function={function}"] + request_args + [f"apikey={self.api_key}"]
        )

        try:
            response = requests.get(request_url)
        except Exception as e:
            self.logger.error(f"Request got generic error '{e}'")
            return None
        response_data: dict[str, any] = response.json()

        if save_result:
            filename = f"{get_utc_timestamp_ms()}" + "__" + "&".join(request_args)
            with open(f"saved_responses/{filename}.json", "w") as file:
                json.dump(response_data, file)

        if "Information" in response_data:
            assert len(response_data) == 1
            self.logger.warning(
                f"Got Information as reponse: '{response_data['Information']}'"
            )
            return None
        if "Error Message" in response_data:
            assert len(response_data) == 1, "'Error Message' key but also other keys!"
            self.logger.warning(
                f"Got the following error response: {response_data['Error Message']}."
            )
            return None
        if data_key is None:
            if "Meta Data" in response_data:
                self.logger.debug("Meta Data: %s", response_data["Meta Data"])
                data_key = [x for x in response_data if x != "Meta Data"]
            else:
                data_key = list(response_data)[0]

        self.logger.debug(
            f"Successfuly sent request '{obfuscate_request_url(request_url, self.api_key)}'"
        )

        return response_data[data_key]
