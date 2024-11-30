import datetime as dt
import json
import logging
import os
from typing import Literal, Optional

import requests
from dotenv import load_dotenv

api_logger = logging.Logger("AV_APIHandler")
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


def format_byte_size(n_bytes: int) -> str:
    if n_bytes >= 1024**3:
        return f"{n_bytes/(1024**3):.2f} GByte"
    elif n_bytes >= 1024**2:
        return f"{n_bytes/(1024**2):.2f} MByte"
    elif n_bytes >= 1024:
        return f"{n_bytes/(1024):.2f} KByte"
    else:
        return f"{n_bytes:.2f} KByte"


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

    def _send_request(
        self,
        function: str,
        request_args: Optional[list[str]] = None,
        save_result: bool = True,
    ) -> Optional[dict[str, any] | list[dict[str, any]]]:
        if request_args is None:
            request_args = []

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
        payload_size = len(response.content)
        self.logger.debug(
            f"'{function}' Payload size: {format_byte_size(payload_size)}."
        )

        response_data: dict[str, any] = response.json()

        if save_result:
            filename = (
                f"{get_utc_timestamp_ms()}" + "__" + "&".join([function] + request_args)
            )
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

        self.logger.debug(
            f"Successfuly sent request '{obfuscate_request_url(request_url, self.api_key)}'"
        )

        return response_data
