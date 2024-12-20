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

    ###############################
    # Time Series Stock Data APIs #
    ###############################

    def get_time_series_intraday(
        self,
        symbol,
        interval,
        adjusted: Optional[any] = None,
        extended_hours: Optional[any] = None,
        month: Optional[any] = None,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#intraday
        This API returns current and 20+ years of historical intraday OHLCV time series of the equity specified, covering pre-market and post-market hours where applicable (e.g., 4:00am to 8:00pm Eastern Time for the US market). You can query both raw (as-traded) and split/dividend-adjusted intraday data from this endpoint. The OHLCV data is sometimes called "candles" in finance literature.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min
        ### adjusted (optional)
        By default, adjusted=true and the output time series is adjusted by historical split and dividend events. Set adjusted=false to query raw (as-traded) intraday values.
        ### extended_hours (optional)
        By default, extended_hours=true and the output time series will include both the regular trading hours and the extended (pre-market and post-market) trading hours (4:00am to 8:00pm Eastern Time for the US market). Set extended_hours=false to query regular trading hours (9:30am to 4:00pm US Eastern Time) only.
        ### month (optional)
        By default, this parameter is not set and the API will return intraday data for the most recent days of trading. You can use the month parameter (in YYYY-MM format) to query a specific month in history. For example, month=2009-01. Any month in the last 20+ years since 2000-01 (January 2000) is supported.
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns trailing 30 days of the most recent intraday data if the month parameter (see above) is not specified, or the full intraday data for a specific month in history if the month parameter is specified. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_INTRADAY",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"adjusted={adjusted}"] if adjusted is not None else [])
            + (
                [f"extended_hours={extended_hours}"]
                if extended_hours is not None
                else []
            )
            + ([f"month={month}"] if month is not None else [])
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_daily(
        self,
        symbol,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#daily
        This API returns raw (as-traded) daily time series (date, daily open, daily high, daily low, daily close, daily volume) of the global equity specified, covering 20+ years of historical data. The OHLCV data is sometimes called "candles" in finance literature. If you are also interested in split/dividend-adjusted data, please use the Daily Adjusted API, which covers adjusted close values and historical split and dividend events.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points; full returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_DAILY",
            request_args=["symbol=symbol"]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_daily_adjusted(
        self,
        symbol,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#dailyadj
        This API returns raw (as-traded) daily open/high/low/close/volume values, adjusted close values, and historical split/dividend events of the global equity specified, covering 20+ years of historical data. The OHLCV data is sometimes called "candles" in finance literature.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points; full returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_DAILY_ADJUSTED",
            request_args=["symbol=symbol"]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_weekly(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#weekly
        This API returns weekly time series (last trading day of each week, weekly open, weekly high, weekly low, weekly close, weekly volume) of the global equity specified, covering 20+ years of historical data.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_WEEKLY",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_weekly_adjusted(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#weeklyadj
        This API returns weekly adjusted time series (last trading day of each week, weekly open, weekly high, weekly low, weekly close, weekly adjusted close, weekly volume, weekly dividend) of the global equity specified, covering 20+ years of historical data.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_WEEKLY_ADJUSTED",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_monthly(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#monthly
        This API returns monthly time series (last trading day of each month, monthly open, monthly high, monthly low, monthly close, monthly volume) of the global equity specified, covering 20+ years of historical data.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_MONTHLY",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_time_series_monthly_adjusted(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#monthlyadj
        This API returns monthly adjusted time series (last trading day of each month, monthly open, monthly high, monthly low, monthly close, monthly adjusted close, monthly volume, monthly dividend) of the equity specified, covering 20+ years of historical data.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TIME_SERIES_MONTHLY_ADJUSTED",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_global_quote(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#latestprice
        This endpoint returns the latest price and volume information for a ticker of your choice. You can specify one ticker per API request.
        If you would like to query a large universe of tickers in bulk, you may want to try out our Realtime Bulk Quotes API, which accepts up to 100 tickers per API request.
        ### symbol (required)
        The symbol of the global ticker of your choice. For example: symbol=IBM.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the quote data in JSON format; csv returns the quote data as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="GLOBAL_QUOTE",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_realtime_bulk_quotes(
        self, symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#realtime-bulk-quotes
        This API returns realtime quotes for US-traded symbols in bulk, accepting up to 100 symbols per API request and covering both regular and extended (pre-market and post-market) trading hours. You can use this endpoint as a high-throughput alternative to the Global Quote API, which accepts one symbol per API request.
        ### symbol (required)
        Up to 100 symbols separated by comma. For example: symbol=MSFT,AAPL,IBM. If more than 100 symbols are provided, only the first 100 symbols will be honored as part of the API input.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the search results in JSON format; csv returns the search results as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="REALTIME_BULK_QUOTES",
            request_args=["symbol=symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_symbol_search(
        self, keywords, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#symbolsearch
        Looking for some specific symbols or companies? Trying to build an auto-complete search box similar to the one below?
        We've got you covered! The Search Endpoint returns the best-matching symbols and market information based on keywords of your choice. The search results also contain match scores that provide you with the full flexibility to develop your own search and filtering logic.
        ### keywords (required)
        A text string of your choice. For example: keywords=microsoft.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the search results in JSON format; csv returns the search results as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="SYMBOL_SEARCH",
            request_args=["keywords=keywords"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_market_status(self, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#market-status
        This endpoint returns the current market status (open vs. closed) of major trading venues for equities, forex, and cryptocurrencies around the world.
        """

        return self._send_request(function="MARKET_STATUS", request_args=[], **kwargs)

    #####################
    # Options Data APIs #
    #####################

    def get_realtime_options(
        self,
        symbol,
        contract: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#realtime-options
        This API returns realtime US options data with full market coverage. Option chains are sorted by expiration dates in chronological order. Within the same expiration date, contracts are sorted by strike prices from low to high.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### contract (optional)
        The US options contract ID you would like to specify. By default, the contract parameter is not set and the entire option chain for a given symbol will be returned.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="REALTIME_OPTIONS",
            request_args=["symbol=symbol"]
            + ([f"contract={contract}"] if contract is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_historical_options(
        self,
        symbol,
        date: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#historical-options
        This API returns the full historical options chain for a specific symbol on a specific date, covering 15+ years of history. Implied volatility (IV) and common Greeks (e.g., delta, gamma, theta, vega, rho) are also returned. Option chains are sorted by expiration dates in chronological order. Within the same expiration date, contracts are sorted by strike prices from low to high.
        ### symbol (required)
        The name of the equity of your choice. For example: symbol=IBM
        ### date (optional)
        By default, the date parameter is not set and the API will return data for the previous trading session. Any date later than 2008-01-01 is accepted. For example, date=2017-11-15.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the options data in JSON format; csv returns the data as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HISTORICAL_OPTIONS",
            request_args=["symbol=symbol"]
            + ([f"date={date}"] if date is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    #######################
    # Alpha Intelligence™ #
    #######################

    def get_news_sentiment(
        self,
        tickers: Optional[any] = None,
        topics: Optional[any] = None,
        time_from: Optional[any] = None,
        sort: Optional[any] = None,
        limit: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#news-sentiment
        Looking for market news data to train your LLM models or to augment your trading strategy? You have just found it. This API returns live and historical market news & sentiment data from a large & growing selection of premier news outlets around the world, covering stocks, cryptocurrencies, forex, and a wide range of topics such as fiscal policy, mergers & acquisitions, IPOs, etc. This API, combined with our core stock API, fundamental data, and technical indicator APIs, can provide you with a 360-degree view of the financial market and the broader economy.
        ### tickers (optional)
        The stock/crypto/forex symbols of your choice. For example: tickers=IBM will filter for articles that mention the IBM ticker; tickers=COIN,CRYPTO:BTC,FOREX:USD will filter for articles that simultaneously mention Coinbase (COIN), Bitcoin (CRYPTO:BTC), and US Dollar (FOREX:USD) in their content.
        ### topics (optional)
        The news topics of your choice. For example: topics=technology will filter for articles that write about the technology sector; topics=technology,ipo will filter for articles that simultaneously cover technology and IPO in their content. Below is the full list of supported topics:
        Blockchain: blockchain
        Earnings: earnings
        IPO: ipo
        Mergers & Acquisitions: mergers_and_acquisitions
        Financial Markets: financial_markets
        Economy - Fiscal Policy (e.g., tax reform, government spending): economy_fiscal
        Economy - Monetary Policy (e.g., interest rates, inflation): economy_monetary
        Economy - Macro/Overall: economy_macro
        Energy & Transportation: energy_transportation
        Finance: finance
        Life Sciences: life_sciences
        Manufacturing: manufacturing
        Real Estate & Construction: real_estate
        Retail & Wholesale: retail_wholesale
        Technology: technology
        ### time_from (optional)
        The time range of the news articles you are targeting, in YYYYMMDDTHHMM format. For example: time_from=20220410T0130. If time_from is specified but time_to is missing, the API will return articles published between the time_from value and the current time.
        ### sort (optional)
        By default, sort=LATEST and the API will return the latest articles first. You can also set sort=EARLIEST or sort=RELEVANCE based on your use case.
        ### limit (optional)
        By default, limit=50 and the API will return up to 50 matching results. You can also set limit=1000 to output up to 1000 results.
        """

        return self._send_request(
            function="NEWS_SENTIMENT",
            request_args=[]
            + ([f"tickers={tickers}"] if tickers is not None else [])
            + ([f"topics={topics}"] if topics is not None else [])
            + ([f"time_from={time_from}"] if time_from is not None else [])
            + ([f"sort={sort}"] if sort is not None else [])
            + ([f"limit={limit}"] if limit is not None else []),
            **kwargs,
        )

    def get_top_gainers_losers(self, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#gainer-loser
        This endpoint returns the top 20 gainers, losers, and the most active traded tickers in the US market.
        """

        return self._send_request(
            function="TOP_GAINERS_LOSERS", request_args=[], **kwargs
        )

    def get_insider_transactions(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#insider-transactions
        This API returns the latest and historical insider transactions made be key stakeholders (e.g., founders, executives, board members, etc.) of a specific company.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="INSIDER_TRANSACTIONS", request_args=["symbol=symbol"], **kwargs
        )

    def get_analytics_fixed_window(
        self,
        SYMBOLS,
        RANGE,
        INTERVAL,
        CALCULATIONS,
        OHLC: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#analytics-fixed-window
        This endpoint returns a rich set of advanced analytics metrics (e.g., total return, variance, auto-correlation, etc.) for a given time series over a fixed temporal window.
        ### SYMBOLS (required)
        A list of symbols for the calculation. It can be a comma separated list of symbols as a string. Free API keys can specify up to 5 symbols per API request. Premium API keys can specify up to 50 symbols per API request.
        ### RANGE (required)
        This is the date range for the series being requested. By default, the date range is the full set of data for the equity history. This can be further modified by the LIMIT variable.
        RANGE can take certain text values as inputs. They are:
        full
        {N}day
        {N}week
        {N}month
        {N}year
        For intraday time series, the following RANGE values are also accepted:
        {N}minute
        {N}hour
        Aside from the “full” value which represents the entire time series, the other values specify an interval to return the series for as measured backwards from the current date/time.
        To specify start & end dates for your analytics calcuation, simply add two RANGE parameters in your API request. For example: RANGE=2023-07-01&RANGE=2023-08-31 or RANGE=2020-12-01T00:04:00&RANGE=2020-12-06T23:59:59 with minute-level precision for intraday analytics. If the end date is missing, the end date is assumed to be the last trading date. In addition, you can request a full month of data by using YYYY-MM format like 2020-12. One day of intraday data can be requested by using YYYY-MM-DD format like 2020-12-06
        ### INTERVAL (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, DAILY, WEEKLY, MONTHLY.
        ### CALCULATIONS (required)
        A comma separated list of the analytics metrics you would like to calculate:
        MIN: The minimum return (largest negative or smallest positive) for all values in the series
        MAX: The maximum return for all values in the series
        MEAN: The mean of all returns in the series
        MEDIAN: The median of all returns in the series
        CUMULATIVE_RETURN: The total return from the beginning to the end of the series range
        VARIANCE: The population variance of returns in the series range. Optionally, you can use VARIANCE(annualized=True)to normalized the output to an annual value. By default, the variance is not annualized.
        STDDEV: The population standard deviation of returns in the series range for each symbol. Optionally, you can use STDDEV(annualized=True)to normalized the output to an annual value. By default, the standard deviation is not annualized.
        MAX_DRAWDOWN: Largest peak to trough interval for each symbol in the series range
        HISTOGRAM: For each symbol, place the observed total returns in bins. By default, bins=10. Use HISTOGRAM(bins=20) to specify a custom bin value (e.g., 20).
        AUTOCORRELATION: For each symbol place, calculate the autocorrelation for the given lag (e.g., the lag in neighboring points for the autocorrelation calculation). By default, lag=1. Use AUTOCORRELATION(lag=2) to specify a custom lag value (e.g., 2).
        COVARIANCE: Returns a covariance matrix for the input symbols. Optionally, you can use COVARIANCE(annualized=True)to normalized the output to an annual value. By default, the covariance is not annualized.
        CORRELATION: Returns a correlation matrix for the input symbols, using the PEARSON method as default. You can also specify the KENDALL or SPEARMAN method through CORRELATION(method=KENDALL) or CORRELATION(method=SPEARMAN), respectively.
        ### OHLC (optional)
        This allows you to choose which open, high, low, or close field the calculation will be performed on. By default, OHLC=close. Valid values for these fields are open, high, low, close.
        """

        return self._send_request(
            function="ANALYTICS_FIXED_WINDOW",
            request_args=[
                "SYMBOLS=SYMBOLS",
                "RANGE=RANGE",
                "INTERVAL=INTERVAL",
                "CALCULATIONS=CALCULATIONS",
            ]
            + ([f"OHLC={OHLC}"] if OHLC is not None else []),
            **kwargs,
        )

    def get_analytics_sliding_window(
        self,
        SYMBOLS,
        RANGE,
        INTERVAL,
        WINDOW_SIZE,
        CALCULATIONS,
        OHLC: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#analytics-sliding-window
        This endpoint returns a rich set of advanced analytics metrics (e.g., total return, variance, auto-correlation, etc.) for a given time series over sliding time windows. For example, we can calculate a moving variance over 5 years with a window of 100 points to see how the variance changes over time.
        ### SYMBOLS (required)
        A list of symbols for the calculation. It can be a comma separated list of symbols as a string. Free API keys can specify up to 5 symbols per API request. Premium API keys can specify up to 50 symbols per API request.
        ### RANGE (required)
        This is the date range for the series being requested. By default, the date range is the full set of data for the equity history. This can be further modified by the LIMIT variable.
        RANGE can take certain text values as inputs. They are:
        full
        {N}day
        {N}week
        {N}month
        {N}year
        For intraday time series, the following RANGE values are also accepted:
        {N}minute
        {N}hour
        Aside from the “full” value which represents the entire time series, the other values specify an interval to return the series for as measured backwards from the current date/time.
        To specify start & end dates for your analytics calcuation, simply add two RANGE parameters in your API request. For example: RANGE=2023-07-01&RANGE=2023-08-31 or RANGE=2020-12-01T00:04:00&RANGE=2020-12-06T23:59:59 with minute-level precision for intraday analytics. If the end date is missing, the end date is assumed to be the last trading date. In addition, you can request a full month of data by using YYYY-MM format like 2020-12. One day of intraday data can be requested by using YYYY-MM-DD format like 2020-12-06
        ### INTERVAL (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, DAILY, WEEKLY, MONTHLY.
        ### WINDOW_SIZE (required)
        An integer representing the size of the moving window. A hard lower boundary of 10 has been set though it is recommended to make this window larger to make sure the running calculations are statistically significant.
        ### CALCULATIONS (required)
        A comma separated list of the analytics metrics you would like to calculate. Free API keys can specify 1 metric to be calculated per API request. Premium API keys can specify multiple metrics to be calculated simultaneously per API request.
        MEAN: The mean of all returns in the series
        MEDIAN: The median of all returns in the series
        CUMULATIVE_RETURN: The total return from the beginning to the end of the series range
        VARIANCE: The population variance of returns in the series range. Optionally, you can use VARIANCE(annualized=True)to normalized the output to an annual value. By default, the variance is not annualized.
        STDDEV: The population standard deviation of returns in the series range for each symbol. Optionally, you can use STDDEV(annualized=True)to normalized the output to an annual value. By default, the standard deviation is not annualized.
        COVARIANCE: Returns a covariance matrix for the input symbols. Optionally, you can use COVARIANCE(annualized=True)to normalized the output to an annual value. By default, the covariance is not annualized.
        CORRELATION: Returns a correlation matrix for the input symbols, using the PEARSON method as default. You can also specify the KENDALL or SPEARMAN method through CORRELATION(method=KENDALL) or CORRELATION(method=SPEARMAN), respectively.
        ### OHLC (optional)
        This allows you to choose which open, high, low, or close field the calculation will be performed on. By default, OHLC=close. Valid values for these fields are open, high, low, close.
        """

        return self._send_request(
            function="ANALYTICS_SLIDING_WINDOW",
            request_args=[
                "SYMBOLS=SYMBOLS",
                "RANGE=RANGE",
                "INTERVAL=INTERVAL",
                "WINDOW_SIZE=WINDOW_SIZE",
                "CALCULATIONS=CALCULATIONS",
            ]
            + ([f"OHLC={OHLC}"] if OHLC is not None else []),
            **kwargs,
        )

    ####################
    # Fundamental Data #
    ####################

    def get_overview(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#company-overview
        This API returns the company information, financial ratios, and other key metrics for the equity specified. Data is generally refreshed on the same day a company reports its latest earnings and financials.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="OVERVIEW", request_args=["symbol=symbol"], **kwargs
        )

    def get_etf_profile(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#etf-profile
        This API returns key ETF metrics (e.g., net assets, expense ratio, and turnover), along with the corresponding ETF holdings / constituents with allocation by asset types and sectors.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=QQQ.
        """

        return self._send_request(
            function="ETF_PROFILE", request_args=["symbol=symbol"], **kwargs
        )

    def get_dividends(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#dividends
        This API returns historical and future (declared) dividend distributions.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="DIVIDENDS", request_args=["symbol=symbol"], **kwargs
        )

    def get_splits(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#splits
        This API returns historical split events.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="SPLITS", request_args=["symbol=symbol"], **kwargs
        )

    def get_income_statement(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#income-statement
        This API returns the annual and quarterly income statements for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="INCOME_STATEMENT", request_args=["symbol=symbol"], **kwargs
        )

    def get_balance_sheet(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#balance-sheet
        This API returns the annual and quarterly balance sheets for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="BALANCE_SHEET", request_args=["symbol=symbol"], **kwargs
        )

    def get_cash_flow(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#cash-flow
        This API returns the annual and quarterly cash flow for the company of interest, with normalized fields mapped to GAAP and IFRS taxonomies of the SEC. Data is generally refreshed on the same day a company reports its latest earnings and financials.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="CASH_FLOW", request_args=["symbol=symbol"], **kwargs
        )

    def get_earnings(self, symbol, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#earnings
        This API returns the annual and quarterly earnings (EPS) for the company of interest. Quarterly data also includes analyst estimates and surprise metrics.
        ### symbol (required)
        The symbol of the ticker of your choice. For example: symbol=IBM.
        """

        return self._send_request(
            function="EARNINGS", request_args=["symbol=symbol"], **kwargs
        )

    def get_listing_status(
        self, date: Optional[any] = None, state: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#listing-status
        This API returns a list of active or delisted US stocks and ETFs, either as of the latest trading day or at a specific time in history. The endpoint is positioned to facilitate equity research on asset lifecycle and survivorship.
        ### date (optional)
        If no date is set, the API endpoint will return a list of active or delisted symbols as of the latest trading day. If a date is set, the API endpoint will "travel back" in time and return a list of active or delisted symbols on that particular date in history. Any YYYY-MM-DD date later than 2010-01-01 is supported. For example, date=2013-08-03
        ### state (optional)
        By default, state=active and the API will return a list of actively traded stocks and ETFs. Set state=delisted to query a list of delisted assets.
        """

        return self._send_request(
            function="LISTING_STATUS",
            request_args=[]
            + ([f"date={date}"] if date is not None else [])
            + ([f"state={state}"] if state is not None else []),
            **kwargs,
        )

    def get_earnings_calendar(
        self, symbol: Optional[any] = None, horizon: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#earnings-calendar
        This API returns a list of company earnings expected in the next 3, 6, or 12 months.
        ### symbol (optional)
        By default, no symbol will be set for this API. When no symbol is set, the API endpoint will return the full list of company earnings scheduled. If a symbol is set, the API endpoint will return the expected earnings for that specific symbol. For example, symbol=IBM
        ### horizon (optional)
        By default, horizon=3month and the API will return a list of expected company earnings in the next 3 months. You may set horizon=6month or horizon=12month to query the earnings scheduled for the next 6 months or 12 months, respectively.
        """

        return self._send_request(
            function="EARNINGS_CALENDAR",
            request_args=[]
            + ([f"symbol={symbol}"] if symbol is not None else [])
            + ([f"horizon={horizon}"] if horizon is not None else []),
            **kwargs,
        )

    def get_ipo_calendar(self, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#ipo-calendar
        This API returns a list of IPOs expected in the next 3 months.
        """

        return self._send_request(function="IPO_CALENDAR", request_args=[], **kwargs)

    ###############################
    # Foreign Exchange Rates (FX) #
    ###############################

    def get_currency_exchange_rate(
        self, from_currency, to_currency, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#currency-exchange
        This API returns the realtime exchange rate for a pair of digital currency (e.g., Bitcoin) and physical currency (e.g., USD).
        ### from_currency (required)
        The currency you would like to get the exchange rate for. It can either be a  physical currency or  digital/crypto currency. For example: from_currency=USD or from_currency=BTC.
        ### to_currency (required)
        The destination currency for the exchange rate. It can either be a  physical currency or  digital/crypto currency. For example: to_currency=USD or to_currency=BTC.
        """

        return self._send_request(
            function="CURRENCY_EXCHANGE_RATE",
            request_args=["from_currency=from_currency", "to_currency=to_currency"],
            **kwargs,
        )

    def get_fx_intraday(
        self,
        from_symbol,
        to_symbol,
        interval,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#fx-intraday
        This API returns intraday time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.
        ### from_symbol (required)
        A three-letter symbol from the  forex currency list. For example: from_symbol=EUR
        ### to_symbol (required)
        A three-letter symbol from the  forex currency list. For example: to_symbol=USD
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns the full-length intraday time series. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="FX_INTRADAY",
            request_args=[
                "from_symbol=from_symbol",
                "to_symbol=to_symbol",
                "interval=interval",
            ]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_fx_daily(
        self,
        from_symbol,
        to_symbol,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#fx-daily
        This API returns the daily time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.
        ### from_symbol (required)
        A three-letter symbol from the  forex currency list. For example: from_symbol=EUR
        ### to_symbol (required)
        A three-letter symbol from the  forex currency list. For example: to_symbol=USD
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the daily time series; full returns the full-length daily time series. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="FX_DAILY",
            request_args=["from_symbol=from_symbol", "to_symbol=to_symbol"]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_fx_weekly(
        self, from_symbol, to_symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#fx-weekly
        This API returns the weekly time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.
        The latest data point is the price information for the week (or partial week) containing the current trading day, updated realtime.
        ### from_symbol (required)
        A three-letter symbol from the  forex currency list. For example: from_symbol=EUR
        ### to_symbol (required)
        A three-letter symbol from the  forex currency list. For example: to_symbol=USD
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the weekly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="FX_WEEKLY",
            request_args=["from_symbol=from_symbol", "to_symbol=to_symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_fx_monthly(
        self, from_symbol, to_symbol, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#fx-monthly
        This API returns the monthly time series (timestamp, open, high, low, close) of the FX currency pair specified, updated realtime.
        The latest data point is the prices information for the month (or partial month) containing the current trading day, updated realtime.
        ### from_symbol (required)
        A three-letter symbol from the  forex currency list. For example: from_symbol=EUR
        ### to_symbol (required)
        A three-letter symbol from the  forex currency list. For example: to_symbol=USD
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the monthly time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="FX_MONTHLY",
            request_args=["from_symbol=from_symbol", "to_symbol=to_symbol"]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    ###############################
    # Digital & Crypto Currencies #
    ###############################

    def get_crypto_intraday(
        self,
        symbol,
        market,
        interval,
        outputsize: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#crypto-intraday
        This API returns intraday time series (timestamp, open, high, low, close, volume) of the cryptocurrency specified, updated realtime.
        ### symbol (required)
        The digital/crypto currency of your choice. It can be any of the currencies in the  digital currency list. For example: symbol=ETH.
        ### market (required)
        The exchange market of your choice. It can be any of the market in the  market list. For example: market=USD.
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min
        ### outputsize (optional)
        By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points in the intraday time series; full returns the full-length intraday time series. The "compact" option is recommended if you would like to reduce the data size of each API call.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the intraday time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="CRYPTO_INTRADAY",
            request_args=["symbol=symbol", "market=market", "interval=interval"]
            + ([f"outputsize={outputsize}"] if outputsize is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_digital_currency_daily(self, symbol, market, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#currency-daily
        This API returns the daily historical time series for a digital currency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.
        ### symbol (required)
        The digital/crypto currency of your choice. It can be any of the currencies in the  digital currency list. For example: symbol=BTC.
        ### market (required)
        The exchange market of your choice. It can be any of the market in the  market list. For example: market=EUR.
        """

        return self._send_request(
            function="DIGITAL_CURRENCY_DAILY",
            request_args=["symbol=symbol", "market=market"],
            **kwargs,
        )

    def get_digital_currency_weekly(self, symbol, market, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#currency-weekly
        This API returns the weekly historical time series for a digital currency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.
        ### symbol (required)
        The digital/crypto currency of your choice. It can be any of the currencies in the  digital currency list. For example: symbol=BTC.
        ### market (required)
        The exchange market of your choice. It can be any of the market in the  market list. For example: market=EUR.
        """

        return self._send_request(
            function="DIGITAL_CURRENCY_WEEKLY",
            request_args=["symbol=symbol", "market=market"],
            **kwargs,
        )

    def get_digital_currency_monthly(self, symbol, market, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#currency-monthly
        This API returns the monthly historical time series for a digital currency (e.g., BTC) traded on a specific market (e.g., EUR/Euro), refreshed daily at midnight (UTC). Prices and volumes are quoted in both the market-specific currency and USD.
        ### symbol (required)
        The digital/crypto currency of your choice. It can be any of the currencies in the  digital currency list. For example: symbol=BTC.
        ### market (required)
        The exchange market of your choice. It can be any of the market in the  market list. For example: market=EUR.
        """

        return self._send_request(
            function="DIGITAL_CURRENCY_MONTHLY",
            request_args=["symbol=symbol", "market=market"],
            **kwargs,
        )

    ###############
    # Commodities #
    ###############

    def get_wti(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#wti
        This API returns the West Texas Intermediate (WTI) crude oil prices in daily, weekly, and monthly horizons.
        Source: U.S. Energy Information Administration, Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings daily, weekly, and monthly are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="WTI",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_brent(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#brent
        This API returns the Brent (Europe) crude oil prices in daily, weekly, and monthly horizons.
        Source: U.S. Energy Information Administration, Crude Oil Prices: Brent - Europe, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings daily, weekly, and monthly are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="BRENT",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_natural_gas(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#natural-gas
        This API returns the Henry Hub natural gas spot prices in daily, weekly, and monthly horizons.
        Source: U.S. Energy Information Administration, Henry Hub Natural Gas Spot Price, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings daily, weekly, and monthly are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="NATURAL_GAS",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_copper(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#copper
        This API returns the global price of copper in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Copper, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="COPPER",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_aluminum(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#aluminum
        This API returns the global price of aluminum in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Aluminum, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ALUMINUM",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_wheat(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#wheat
        This API returns the global price of wheat in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Wheat, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="WHEAT",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_corn(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#corn
        This API returns the global price of corn in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Corn, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="CORN",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_cotton(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#cotton
        This API returns the global price of cotton in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Cotton, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="COTTON",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_sugar(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#sugar
        This API returns the global price of sugar in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Sugar, No. 11, World, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="SUGAR",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_coffee(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#coffee
        This API returns the global price of coffee in monthly, quarterly, and annual horizons.
        Source: International Monetary Fund (IMF Terms of Use), Global price of Coffee, Other Mild Arabica, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="COFFEE",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_all_commodities(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#all-commodities
        This API returns the global price index of all commodities in monthly, quarterly, and annual temporal dimensions.
        Source: International Monetary Fund (IMF Terms of Use), Global Price Index of All Commodities, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly, quarterly, and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ALL_COMMODITIES",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    #######################
    # Economic Indicators #
    #######################

    def get_real_gdp(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#real-gdp
        This API returns the annual and quarterly Real GDP of the United States.
        Source: U.S. Bureau of Economic Analysis, Real Gross Domestic Product, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=annual. Strings quarterly and annual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="REAL_GDP",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_real_gdp_per_capita(
        self, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#real-gdp-per-capita
        This API returns the quarterly Real GDP per Capita data of the United States.
        Source: U.S. Bureau of Economic Analysis, Real gross domestic product per capita, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="REAL_GDP_PER_CAPITA",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_treasury_yield(
        self,
        interval: Optional[any] = None,
        maturity: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#treasury-yield
        This API returns the daily, weekly, and monthly US treasury yield of a given maturity timeline (e.g., 5 year, 30 year, etc).
        Source: Board of Governors of the Federal Reserve System (US), Market Yield on U.S. Treasury Securities at 3-month, 2-year, 5-year, 7-year, 10-year, and 30-year Constant Maturities, Quoted on an Investment Basis, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings daily, weekly, and monthly are accepted.
        ### maturity (optional)
        By default, maturity=10year. Strings 3month, 2year, 5year, 7year, 10year, and 30year are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TREASURY_YIELD",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"maturity={maturity}"] if maturity is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_federal_funds_rate(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#interest-rate
        This API returns the daily, weekly, and monthly federal funds rate (interest rate) of the United States.
        Source: Board of Governors of the Federal Reserve System (US), Federal Funds Effective Rate, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/FEDFUNDS). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings daily, weekly, and monthly are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="FEDERAL_FUNDS_RATE",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_cpi(
        self, interval: Optional[any] = None, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#cpi
        This API returns the monthly and semiannual consumer price index (CPI) of the United States. CPI is widely regarded as the barometer of inflation levels in the broader economy.
        Source: U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers: All Items in U.S. City Average, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### interval (optional)
        By default, interval=monthly. Strings monthly and semiannual are accepted.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="CPI",
            request_args=[]
            + ([f"interval={interval}"] if interval is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_inflation(self, datatype: Optional[any] = None, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#inflation
        This API returns the annual inflation rates (consumer prices) of the United States.
        Source: World Bank, Inflation, consumer prices for the United States, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="INFLATION",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_retail_sales(
        self, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#retail-sales
        This API returns the monthly Advance Retail Sales: Retail Trade data of the United States.
        Source: U.S. Census Bureau, Advance Retail Sales: Retail Trade, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/RSXFSN). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="RETAIL_SALES",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_durables(self, datatype: Optional[any] = None, **kwargs) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#durable-goods
        This API returns the monthly manufacturers' new orders of durable goods in the United States.
        Source: U.S. Census Bureau, Manufacturers' New Orders: Durable Goods, retrieved from FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org/series/UMDMNO). This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="DURABLES",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_unemployment(
        self, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#unemployment
        This API returns the monthly unemployment data of the United States. The unemployment rate represents the number of unemployed as a percentage of the labor force. Labor force data are restricted to people 16 years of age and older, who currently reside in 1 of the 50 states or the District of Columbia, who do not reside in institutions (e.g., penal and mental facilities, homes for the aged), and who are not on active duty in the Armed Forces (source).
        Source: U.S. Bureau of Labor Statistics, Unemployment Rate, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="UNEMPLOYMENT",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_nonfarm_payroll(
        self, datatype: Optional[any] = None, **kwargs
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#nonfarm-payroll
        This API returns the monthly US All Employees: Total Nonfarm (commonly known as Total Nonfarm Payroll), a measure of the number of U.S. workers in the economy that excludes proprietors, private household employees, unpaid volunteers, farm employees, and the unincorporated self-employed.
        Source: U.S. Bureau of Labor Statistics, All Employees, Total Nonfarm, retrieved from FRED, Federal Reserve Bank of St. Louis. This data feed uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis. By using this data feed, you agree to be bound by the FRED® API Terms of Use.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="NONFARM_PAYROLL",
            request_args=[]
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    ########################
    # Technical Indicators #
    ########################

    def get_sma(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#sma
        This API returns the simple moving average (SMA) values. See also: SMA explainer and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="SMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ema(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#ema
        This API returns the exponential moving average (EMA) values. See also: EMA explainer and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="EMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_wma(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#wma
        This API returns the weighted moving average (WMA) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="WMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_dema(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#dema
        This API returns the double exponential moving average (DEMA) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="DEMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_tema(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#tema
        This API returns the triple exponential moving average (TEMA) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TEMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_trima(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#trima
        This API returns the triangular moving average (TRIMA) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TRIMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_kama(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#kama
        This API returns the Kaufman adaptive moving average (KAMA) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="KAMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_mama(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        fastlimit: Optional[any] = None,
        slowlimit: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#mama
        This API returns the MESA adaptive moving average (MAMA) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastlimit (optional)
        Positive floats are accepted. By default, fastlimit=0.01.
        ### slowlimit (optional)
        Positive floats are accepted. By default, slowlimit=0.01.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MAMA",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastlimit={fastlimit}"] if fastlimit is not None else [])
            + ([f"slowlimit={slowlimit}"] if slowlimit is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_vwap(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#vwap
        This API returns the volume weighted average price (VWAP) for intraday time series. See also: Investopedia article.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. In keeping with mainstream investment literatures on VWAP, the following intraday intervals are supported: 1min, 5min, 15min, 30min, 60min
        ### month (optional)
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="VWAP",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_t3(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#t3
        This API returns the triple exponential moving average (T3) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each moving average value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="T3",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_macd(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        fastperiod: Optional[any] = None,
        slowperiod: Optional[any] = None,
        signalperiod: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#macd
        This API returns the moving average convergence / divergence (MACD) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastperiod (optional)
        Positive integers are accepted. By default, fastperiod=12.
        ### slowperiod (optional)
        Positive integers are accepted. By default, slowperiod=26.
        ### signalperiod (optional)
        Positive integers are accepted. By default, signalperiod=9.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MACD",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"signalperiod={signalperiod}"] if signalperiod is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_macdext(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        fastperiod: Optional[any] = None,
        slowperiod: Optional[any] = None,
        signalperiod: Optional[any] = None,
        fastmatype: Optional[any] = None,
        slowmatype: Optional[any] = None,
        signalmatype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#macdext
        This API returns the moving average convergence / divergence values with controllable moving average type. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastperiod (optional)
        Positive integers are accepted. By default, fastperiod=12.
        ### slowperiod (optional)
        Positive integers are accepted. By default, slowperiod=26.
        ### signalperiod (optional)
        Positive integers are accepted. By default, signalperiod=9.
        ### fastmatype (optional)
        Moving average type for the faster moving average. By default, fastmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### slowmatype (optional)
        Moving average type for the slower moving average. By default, slowmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### signalmatype (optional)
        Moving average type for the signal moving average. By default, signalmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MACDEXT",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"signalperiod={signalperiod}"] if signalperiod is not None else [])
            + ([f"fastmatype={fastmatype}"] if fastmatype is not None else [])
            + ([f"slowmatype={slowmatype}"] if slowmatype is not None else [])
            + ([f"signalmatype={signalmatype}"] if signalmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_stoch(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        fastkperiod: Optional[any] = None,
        slowkperiod: Optional[any] = None,
        slowdperiod: Optional[any] = None,
        slowkmatype: Optional[any] = None,
        slowdmatype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#stoch
        This API returns the stochastic oscillator (STOCH) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastkperiod (optional)
        The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.
        ### slowkperiod (optional)
        The time period of the slowk moving average. Positive integers are accepted. By default, slowkperiod=3.
        ### slowdperiod (optional)
        The time period of the slowd moving average. Positive integers are accepted. By default, slowdperiod=3.
        ### slowkmatype (optional)
        Moving average type for the slowk moving average. By default, slowkmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### slowdmatype (optional)
        Moving average type for the slowd moving average. By default, slowdmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="STOCH",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"slowkperiod={slowkperiod}"] if slowkperiod is not None else [])
            + ([f"slowdperiod={slowdperiod}"] if slowdperiod is not None else [])
            + ([f"slowkmatype={slowkmatype}"] if slowkmatype is not None else [])
            + ([f"slowdmatype={slowdmatype}"] if slowdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_stochf(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        fastkperiod: Optional[any] = None,
        fastdperiod: Optional[any] = None,
        fastdmatype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#stochf
        This API returns the stochastic fast (STOCHF) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastkperiod (optional)
        The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.
        ### fastdperiod (optional)
        The time period of the fastd moving average. Positive integers are accepted. By default, fastdperiod=3.
        ### fastdmatype (optional)
        Moving average type for the fastd moving average. By default, fastdmatype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="STOCHF",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"fastdperiod={fastdperiod}"] if fastdperiod is not None else [])
            + ([f"fastdmatype={fastdmatype}"] if fastdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_rsi(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#rsi
        This API returns the relative strength index (RSI) values. See also: RSI explainer and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each RSI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="RSI",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_stochrsi(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        fastkperiod: Optional[any] = None,
        fastdperiod: Optional[any] = None,
        fastdmatype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#stochrsi
        This API returns the stochastic relative strength index (STOCHRSI) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each STOCHRSI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### fastkperiod (optional)
        The time period of the fastk moving average. Positive integers are accepted. By default, fastkperiod=5.
        ### fastdperiod (optional)
        The time period of the fastd moving average. Positive integers are accepted. By default, fastdperiod=3.
        ### fastdmatype (optional)
        Moving average type for the fastd moving average. By default, fastdmatype=0. Integers 0 - 8 are accepted with the following mappings.  0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="STOCHRSI",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"fastkperiod={fastkperiod}"] if fastkperiod is not None else [])
            + ([f"fastdperiod={fastdperiod}"] if fastdperiod is not None else [])
            + ([f"fastdmatype={fastdmatype}"] if fastdmatype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_willr(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#willr
        This API returns the Williams' %R (WILLR) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each WILLR value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="WILLR",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_adx(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#adx
        This API returns the average directional movement index (ADX) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each ADX value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ADX",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_adxr(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#adxr
        This API returns the average directional movement index rating (ADXR) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each ADXR value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ADXR",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_apo(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        fastperiod: Optional[any] = None,
        slowperiod: Optional[any] = None,
        matype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#apo
        This API returns the absolute price oscillator (APO) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastperiod (optional)
        Positive integers are accepted. By default, fastperiod=12.
        ### slowperiod (optional)
        Positive integers are accepted. By default, slowperiod=26.
        ### matype (optional)
        Moving average type. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="APO",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ppo(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        fastperiod: Optional[any] = None,
        slowperiod: Optional[any] = None,
        matype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#ppo
        This API returns the percentage price oscillator (PPO) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastperiod (optional)
        Positive integers are accepted. By default, fastperiod=12.
        ### slowperiod (optional)
        Positive integers are accepted. By default, slowperiod=26.
        ### matype (optional)
        Moving average type. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="PPO",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_mom(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#mom
        This API returns the momentum (MOM) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MOM value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MOM",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_bop(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#bop
        This API returns the balance of power (BOP) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="BOP",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_cci(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#cci
        This API returns the commodity channel index (CCI) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each CCI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="CCI",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_cmo(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#cmo
        This API returns the Chande momentum oscillator (CMO) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each CMO value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="CMO",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_roc(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#roc
        This API returns the rate of change (ROC) values. See also: Investopedia article.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each ROC value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ROC",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_rocr(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#rocr
        This API returns the rate of change ratio (ROCR) values. See also: Investopedia article.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each ROCR value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ROCR",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_aroon(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#aroon
        This API returns the Aroon (AROON) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each AROON value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="AROON",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_aroonosc(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#aroonosc
        This API returns the Aroon oscillator (AROONOSC) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each AROONOSC value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="AROONOSC",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_mfi(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#mfi
        This API returns the money flow index (MFI) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MFI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MFI",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_trix(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#trix
        This API returns the 1-day rate of change of a triple smooth exponential moving average (TRIX) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each TRIX value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TRIX",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ultosc(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        timeperiod1: Optional[any] = None,
        timeperiod2: Optional[any] = None,
        timeperiod3: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#ultosc
        This API returns the ultimate oscillator (ULTOSC) values. See also: mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### timeperiod1 (optional)
        The first time period for the indicator. Positive integers are accepted. By default, timeperiod1=7.
        ### timeperiod2 (optional)
        The second time period for the indicator. Positive integers are accepted. By default, timeperiod2=14.
        ### timeperiod3 (optional)
        The third time period for the indicator. Positive integers are accepted. By default, timeperiod3=28.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ULTOSC",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"timeperiod1={timeperiod1}"] if timeperiod1 is not None else [])
            + ([f"timeperiod2={timeperiod2}"] if timeperiod2 is not None else [])
            + ([f"timeperiod3={timeperiod3}"] if timeperiod3 is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_dx(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#dx
        This API returns the directional movement index (DX) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each DX value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="DX",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_minus_di(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#minusdi
        This API returns the minus directional indicator (MINUS_DI) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MINUS_DI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MINUS_DI",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_plus_di(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#plusdi
        This API returns the plus directional indicator (PLUS_DI) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each PLUS_DI value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="PLUS_DI",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_minus_dm(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#minusdm
        This API returns the minus directional movement (MINUS_DM) values. See also: Investopedia article
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MINUS_DM value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MINUS_DM",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_plus_dm(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#plusdm
        This API returns the plus directional movement (PLUS_DM) values. See also: Investopedia article
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each PLUS_DM value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="PLUS_DM",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_bbands(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        nbdevup: Optional[any] = None,
        nbdevdn: Optional[any] = None,
        matype: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#bbands
        This API returns the Bollinger bands (BBANDS) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each BBANDS value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### nbdevup (optional)
        The standard deviation multiplier of the upper band. Positive integers are accepted. By default, nbdevup=2.
        ### nbdevdn (optional)
        The standard deviation multiplier of the lower band. Positive integers are accepted. By default, nbdevdn=2.
        ### matype (optional)
        Moving average type of the time series. By default, matype=0. Integers 0 - 8 are accepted with the following mappings. 0 = Simple Moving Average (SMA), 1 = Exponential Moving Average (EMA), 2 = Weighted Moving Average (WMA), 3 = Double Exponential Moving Average (DEMA), 4 = Triple Exponential Moving Average (TEMA), 5 = Triangular Moving Average (TRIMA), 6 = T3 Moving Average, 7 = Kaufman Adaptive Moving Average (KAMA), 8 = MESA Adaptive Moving Average (MAMA).
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="BBANDS",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"nbdevup={nbdevup}"] if nbdevup is not None else [])
            + ([f"nbdevdn={nbdevdn}"] if nbdevdn is not None else [])
            + ([f"matype={matype}"] if matype is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_midpoint(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#midpoint
        This API returns the midpoint (MIDPOINT) values. MIDPOINT = (highest value + lowest value)/2.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MIDPOINT value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MIDPOINT",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_midprice(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#midprice
        This API returns the midpoint price (MIDPRICE) values. MIDPRICE = (highest high + lowest low)/2.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each MIDPRICE value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="MIDPRICE",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_sar(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        acceleration: Optional[any] = None,
        maximum: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#sar
        This API returns the parabolic SAR (SAR) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### acceleration (optional)
        The acceleration factor. Positive floats are accepted. By default, acceleration=0.01.
        ### maximum (optional)
        The acceleration factor maximum value. Positive floats are accepted. By default, maximum=0.20.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="SAR",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"acceleration={acceleration}"] if acceleration is not None else [])
            + ([f"maximum={maximum}"] if maximum is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_trange(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#trange
        This API returns the true range (TRANGE) values. See also: mathematical reference
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="TRANGE",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_atr(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#atr
        This API returns the average true range (ATR) values. See also: Investopedia article and mathematical reference
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each ATR value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ATR",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_natr(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        time_period: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#natr
        This API returns the normalized average true range (NATR) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### time_period (optional)
        Number of data points used to calculate each NATR value. Positive integers are accepted (e.g., time_period=60, time_period=200)
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="NATR",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"time_period={time_period}"] if time_period is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ad(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#ad
        This API returns the Chaikin A/D line (AD) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="AD",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_adosc(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        fastperiod: Optional[any] = None,
        slowperiod: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#adosc
        This API returns the Chaikin A/D oscillator (ADOSC) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### fastperiod (optional)
        The time period of the fast EMA. Positive integers are accepted. By default, fastperiod=3.
        ### slowperiod (optional)
        The time period of the slow EMA. Positive integers are accepted. By default, slowperiod=10.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="ADOSC",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"fastperiod={fastperiod}"] if fastperiod is not None else [])
            + ([f"slowperiod={slowperiod}"] if slowperiod is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_obv(
        self,
        symbol,
        interval,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#obv
        This API returns the on balance volume (OBV) values. See also: Investopedia article and mathematical reference.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="OBV",
            request_args=["symbol=symbol", "interval=interval"]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_trendline(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#httrendline
        This API returns the Hilbert transform, instantaneous trendline (HT_TRENDLINE) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_TRENDLINE",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_sine(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#htsine
        This API returns the Hilbert transform, sine wave (HT_SINE) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_SINE",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_trendmode(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#httrendmode
        This API returns the Hilbert transform, trend vs cycle mode (HT_TRENDMODE) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_TRENDMODE",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_dcperiod(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#htdcperiod
        This API returns the Hilbert transform, dominant cycle period (HT_DCPERIOD) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_DCPERIOD",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_dcphase(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#htdcphase
        This API returns the Hilbert transform, dominant cycle phase (HT_DCPHASE) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_DCPHASE",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )

    def get_ht_phasor(
        self,
        symbol,
        interval,
        series_type,
        month: Optional[any] = None,
        datatype: Optional[any] = None,
        **kwargs,
    ) -> dict[str, any]:
        """
        https://www.alphavantage.co/documentation/#htphasor
        This API returns the Hilbert transform, phasor components (HT_PHASOR) values.
        ### symbol (required)
        The name of the ticker of your choice. For example: symbol=IBM
        ### interval (required)
        Time interval between two consecutive data points in the time series. The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
        ### series_type (required)
        The desired price type in the time series. Four types are supported: close, open, high, low
        ### month (optional)
        Note: this parameter is ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets. The daily/weekly/monthly intervals are agnostic to this parameter.
        By default, this parameter is not set and the technical indicator values will be calculated based on the most recent 30 days of intraday data. You can use the month parameter (in YYYY-MM format) to compute intraday technical indicators for a specific month in history. For example, month=2009-01. Any month equal to or later than 2000-01 (January 2000) is supported.
        ### datatype (optional)
        By default, datatype=json. Strings json and csv are accepted with the following specifications: json returns the daily time series in JSON format; csv returns the time series as a CSV (comma separated value) file.
        """

        return self._send_request(
            function="HT_PHASOR",
            request_args=[
                "symbol=symbol",
                "interval=interval",
                "series_type=series_type",
            ]
            + ([f"month={month}"] if month is not None else [])
            + ([f"datatype={datatype}"] if datatype is not None else []),
            **kwargs,
        )
