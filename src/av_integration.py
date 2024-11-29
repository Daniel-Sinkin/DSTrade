import datetime as dt
import json
import logging
import os
from enum import StrEnum, auto
from typing import Literal, Optional

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

api_logger = logging.Logger("APIHandler")
api_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

api_logger.addHandler(stream_handler)


class AV_TICKER(StrEnum):
    IBM = "IBM"
    TSCO_LON = "TSCO.LON"
    SHOP_TRT = "SHOP.TRT"
    GPV_TRV = "GPV.TRV"
    MBG_DEX = "MBG.DEX"
    RELIANCE_BSE = "RELIANCE.BSE"
    _600104_SHH = "600104.SHH"
    _000002_SHZ = "000002.SHZ"


class AV_CANDLE_TF(StrEnum):
    MIN = "1min"
    MIN5 = "5min"
    MIN15 = "15min"
    MIN30 = "30min"
    HOUR = "60min"


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
        symbol: AV_TICKER | str,
        outputsize: Literal["full", "compact"] = "compact",
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[pd.DataFrame]:
        function = "TIME_SERIES_DAILY"
        data = self.send_request(
            function=function,
            request_args=[f"symbol={symbol}"]
            + ([f"outputsize={outputsize}"] if outputsize != "compact" else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
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
        symbol: AV_TICKER,
        interval: AV_CANDLE_TF,
        adjusted: bool = True,
        extended_hours: bool = True,
        month: Optional[str] = None,
        outputsize: Literal["compact", "full"] = "compact",
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> pd.DataFrame:
        function = "TIME_SERIES_INTRADAY"
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

    def send_request(
        self,
        function: str,
        request_args: list[str],
        save_result: bool = False,
        log_metadata: bool = False,
    ) -> Optional[dict[str, any]]:
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
        assert "Meta Data" in response_data, "Successful responses should have metadata"
        if log_metadata:
            self.logger.info("Meta Data: %s", response_data["Meta Data"])
        assert (
            len(response_data) == 2
        ), "Successful responses should have exactly 2 keys"

        self.logger.debug(
            f"Successfuly sent request '{obfuscate_request_url(request_url, self.api_key)}'"
        )
        if save_result:
            filename = f"{get_utc_timestamp_ms()}" + "__" + "&".join(request_args)
            with open(f"saved_responses/{filename}.json", "w") as file:
                json.dump(response_data, file)

        # The other key aside from 'Meta Data'
        content_key = [k for k in response_data.keys() if k != "Meta Data"][0]

        return response_data[content_key]


def get_data() -> None:
    alpha_vantage_api_handler = AlphaVantageAPIHandler(api_key="demo")
    data = alpha_vantage_api_handler.get_time_series_daily(
        AV_TICKER.IBM, outputsize="full", save_result=True, log_metadata=True
    )
    if data is None:
        api_logger.warning("Received no data, aborting!")
        return

    data.to_pickle("test.pkl")


if __name__ == "__main__":
    get_data()
    df: pd.DataFrame = pd.read_pickle("test.pkl")
    print(df)
    print(df.dtypes)
    print(str(AV_TICKER.IBM))
