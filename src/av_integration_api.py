import datetime as dt
import json
import logging
import os
from typing import Literal, Optional

import requests
from dotenv import load_dotenv

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
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.url_base = "https://www.alphavantage.co/"
        self.url_request = self.url_base + "query?"

        self.logger = api_logger

        self.logger.debug(f"Created {self}.")

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

    def get_time_series_intraday(
        self,
        symbol,
        interval,
        adjusted=None,
        extended_hours=None,
        month=None,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_INTRADAY",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"adjusted={adjusted}"] if adjusted is not None else [])
            + (
                [f"extended_hours={extended_hours}"]
                if extended_hours is not None
                else []
            )
            + ([f"month={month}"] if month is not None else [])
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_daily(
        self,
        symbol,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_DAILY",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_daily_adjusted(
        self,
        symbol,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_DAILY_ADJUSTED",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_weekly(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_WEEKLY",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_weekly_adjusted(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_WEEKLY_ADJUSTED",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_monthly(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_MONTHLY",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_time_series_monthly_adjusted(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TIME_SERIES_MONTHLY_ADJUSTED",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_realtime_bulk_quotes(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="REALTIME_BULK_QUOTES",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_symbol_search(
        self, keywords, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="SYMBOL_SEARCH",
            request_args=[
                f"keywords={keywords}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_realtime_options(
        self, symbol, contract=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="REALTIME_OPTIONS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"contract={contract}"] if contract is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_historical_options(
        self, symbol, date=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HISTORICAL_OPTIONS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"date={date}"] if date is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_news_sentiment(
        self,
        tickers=None,
        topics=None,
        time_from=None,
        time_to=None,
        sort=None,
        limit=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="NEWS_SENTIMENT",
            request_args=[]
            + ([f"tickers={tickers}"] if tickers is not None else [])
            + ([f"topics={topics}"] if topics is not None else [])
            + ([f"time_from={time_from}"] if time_from is not None else [])
            + ([f"time_to={time_to}"] if time_to is not None else [])
            + ([f"sort={sort}"] if sort is not None else [])
            + ([f"limit={limit}"] if limit is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_insider_transactions(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="INSIDER_TRANSACTIONS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_analytics_sliding_window(
        self,
        SYMBOLS,
        RANGE,
        INTERVAL,
        WINDOW_SIZE,
        CALCULATIONS,
        OHLC=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ANALYTICS_SLIDING_WINDOW",
            request_args=[
                f"SYMBOLS={SYMBOLS}",
                f"RANGE={RANGE}",
                f"INTERVAL={INTERVAL}",
                f"WINDOW_SIZE={WINDOW_SIZE}",
                f"CALCULATIONS={CALCULATIONS}",
            ]
            + ([f"OHLC={OHLC}"] if OHLC is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_overview(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="OVERVIEW",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_etf_profile(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ETF_PROFILE",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_dividends(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DIVIDENDS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_splits(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="SPLITS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_income_statement(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="INCOME_STATEMENT",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_balance_sheet(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="BALANCE_SHEET",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_cash_flow(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CASH_FLOW",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_earnings(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="EARNINGS",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_listing_status(
        self, date=None, state=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="LISTING_STATUS",
            request_args=[]
            + ([f"date={date}"] if date is not None else [])
            + ([f"state={state}"] if state is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_earnings_calendar(
        self,
        symbol=None,
        horizon=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="EARNINGS_CALENDAR",
            request_args=[]
            + ([f"symbol={symbol}"] if symbol is not None else [])
            + ([f"horizon={horizon}"] if horizon is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_currency_exchange_rate(
        self,
        from_currency,
        to_currency,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CURRENCY_EXCHANGE_RATE",
            request_args=[
                f"from_currency={from_currency}",
                f"to_currency={to_currency}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_fx_intraday(
        self,
        from_symbol,
        to_symbol,
        interval,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="FX_INTRADAY",
            request_args=[
                f"from_symbol={from_symbol}",
                f"to_symbol={to_symbol}",
                f"interval={interval}",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_fx_daily(
        self,
        from_symbol,
        to_symbol,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="FX_DAILY",
            request_args=[
                f"from_symbol={from_symbol}",
                f"to_symbol={to_symbol}",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_fx_weekly(
        self,
        from_symbol,
        to_symbol,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="FX_WEEKLY",
            request_args=[
                f"from_symbol={from_symbol}",
                f"to_symbol={to_symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_fx_monthly(
        self,
        from_symbol,
        to_symbol,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="FX_MONTHLY",
            request_args=[
                f"from_symbol={from_symbol}",
                f"to_symbol={to_symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_crypto_intraday(
        self,
        symbol,
        market,
        interval,
        outputsize=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CRYPTO_INTRADAY",
            request_args=[
                f"symbol={symbol}",
                f"market={market}",
                f"interval={interval}",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_digital_currency_daily(
        self, symbol, market, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DIGITAL_CURRENCY_DAILY",
            request_args=[
                f"symbol={symbol}",
                f"market={market}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_digital_currency_weekly(
        self, symbol, market, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DIGITAL_CURRENCY_WEEKLY",
            request_args=[
                f"symbol={symbol}",
                f"market={market}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_digital_currency_monthly(
        self, symbol, market, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DIGITAL_CURRENCY_MONTHLY",
            request_args=[
                f"symbol={symbol}",
                f"market={market}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_wti(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="WTI",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_brent(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="BRENT",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_natural_gas(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="NATURAL_GAS",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_copper(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="COPPER",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_aluminum(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ALUMINUM",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_wheat(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="WHEAT",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_corn(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CORN",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_cotton(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="COTTON",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_sugar(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="SUGAR",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_coffee(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="COFFEE",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_all_commodities(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ALL_COMMODITIES",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_real_gdp(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="REAL_GDP",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_treasury_yield(
        self,
        interval=None,
        maturity=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TREASURY_YIELD",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"maturity={maturity}"] if maturity is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_federal_funds_rate(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="FEDERAL_FUNDS_RATE",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_cpi(
        self, interval=None, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CPI",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_sma(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="SMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ema(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="EMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_wma(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="WMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_dema(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DEMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_tema(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TEMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_trima(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TRIMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_kama(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="KAMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_mama(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        fastlimit=None,
        slowlimit=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MAMA",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastlimit={fastlimit}"] if fastlimit is not None else [])
            + ([f"slowlimit={slowlimit}"] if slowlimit is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_vwap(
        self,
        symbol,
        interval,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="VWAP",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_t3(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="T3",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_macd(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        fastperiod=None,
        slowperiod=None,
        signalperiod=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MACD",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"signalperiod={signalperiod}"] if signalperiod is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_macdext(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        fastperiod=None,
        slowperiod=None,
        signalperiod=None,
        fastmatype=None,
        slowmatype=None,
        signalmatype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MACDEXT",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"signalperiod={signalperiod}"] if signalperiod is not None else [])
            + ([f"fastmatype={fastmatype}"] if fastmatype is not None else [])
            + ([f"slowmatype={slowmatype}"] if slowmatype is not None else [])
            + ([f"signalmatype={signalmatype}"] if signalmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_stoch(
        self,
        symbol,
        interval,
        month=None,
        fastkperiod=None,
        slowkperiod=None,
        slowdperiod=None,
        slowkmatype=None,
        slowdmatype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="STOCH",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"slowkperiod={slowkperiod}"] if slowkperiod is not None else [])
            + ([f"slowdperiod={slowdperiod}"] if slowdperiod is not None else [])
            + ([f"slowkmatype={slowkmatype}"] if slowkmatype is not None else [])
            + ([f"slowdmatype={slowdmatype}"] if slowdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_stochf(
        self,
        symbol,
        interval,
        month=None,
        fastkperiod=None,
        fastdperiod=None,
        fastdmatype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="STOCHF",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"fastdperiod={fastdperiod}"] if fastdperiod is not None else [])
            + ([f"fastdmatype={fastdmatype}"] if fastdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_rsi(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="RSI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_stochrsi(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        fastkperiod=None,
        fastdperiod=None,
        fastdmatype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="STOCHRSI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"fastdperiod={fastdperiod}"] if fastdperiod is not None else [])
            + ([f"fastdmatype={fastdmatype}"] if fastdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_willr(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="WILLR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_adx(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ADX",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_adxr(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ADXR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_apo(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        fastperiod=None,
        slowperiod=None,
        matype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="APO",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ppo(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        fastperiod=None,
        slowperiod=None,
        matype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="PPO",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_mom(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MOM",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_bop(
        self,
        symbol,
        interval,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="BOP",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_cci(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CCI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_cmo(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="CMO",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_roc(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ROC",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_rocr(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ROCR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_aroon(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="AROON",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_aroonosc(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="AROONOSC",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_mfi(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MFI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_trix(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TRIX",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ultosc(
        self,
        symbol,
        interval,
        month=None,
        timeperiod1=None,
        timeperiod2=None,
        timeperiod3=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ULTOSC",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"timeperiod1={timeperiod1}"] if timeperiod1 is not None else [])
            + ([f"timeperiod2={timeperiod2}"] if timeperiod2 is not None else [])
            + ([f"timeperiod3={timeperiod3}"] if timeperiod3 is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_dx(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DX",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_minus_di(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MINUS_DI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_plus_di(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="PLUS_DI",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_minus_dm(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MINUS_DM",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_plus_dm(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="PLUS_DM",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_bbands(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        nbdevup=None,
        nbdevdn=None,
        matype=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="BBANDS",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"nbdevup={nbdevup}"] if nbdevup is not None else [])
            + ([f"nbdevdn={nbdevdn}"] if nbdevdn is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_midpoint(
        self,
        symbol,
        interval,
        time_period,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MIDPOINT",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_midprice(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="MIDPRICE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_sar(
        self,
        symbol,
        interval,
        month=None,
        acceleration=None,
        maximum=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="SAR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"acceleration={acceleration}"] if acceleration is not None else [])
            + ([f"maximum={maximum}"] if maximum is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_trange(
        self,
        symbol,
        interval,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="TRANGE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_atr(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ATR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_natr(
        self,
        symbol,
        interval,
        time_period,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="NATR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"time_period={time_period}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ad(
        self,
        symbol,
        interval,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="AD",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_adosc(
        self,
        symbol,
        interval,
        month=None,
        fastperiod=None,
        slowperiod=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="ADOSC",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_obv(
        self,
        symbol,
        interval,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="OBV",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_trendline(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_TRENDLINE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_sine(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_SINE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_trendmode(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_TRENDMODE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_dcperiod(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_DCPERIOD",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_dcphase(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_DCPHASE",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_ht_phasor(
        self,
        symbol,
        interval,
        series_type,
        month=None,
        datatype: Literal["json", "csv"] = "json",
        **kwargs,
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="HT_PHASOR",
            request_args=[
                f"symbol={symbol}",
                f"interval={interval}",
                f"series_type={series_type}",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_analytics_fixed_window(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "The multiple RANGE argument is currently not supported!"
        )

    def get_global_quote(
        self, symbol, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="GLOBAL_QUOTE",
            request_args=[
                f"symbol={symbol}",
            ]
            + ([f"datatype={datatype}"] if datatype != "json" else []),
        )

    def get_market_status(self, **kwargs) -> Optional[dict[str, any]]:
        return self._send_request(function="MARKET_STATUS", **kwargs)

    def get_top_gainers_losers(self, **kwargs) -> Optional[dict[str, any]]:
        return self._send_request(function="TOP_GAINERS_LOSERS", **kwargs)

    def get_real_gdp_per_capita(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="REAL_GDP_PER_CAPITA",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_inflation(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="INFLATION",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_retail_sales(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="RETAIL_SALES",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_durables(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="DURABLES",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_unemployment(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="UNEMPLOYMENT",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )

    def get_nonfarm_payroll(
        self, datatype: Literal["json", "csv"] = "json", **kwargs
    ) -> Optional[dict[str, any]]:
        return self._send_request(
            function="NONFARM_PAYROLL",
            request_args=[] + ([f"datatype={datatype}"] if datatype != "json" else []),
            **kwargs,
        )
