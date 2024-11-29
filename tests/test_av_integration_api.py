from src.av_integration import AlphaVantageAPIHandler

handler = AlphaVantageAPIHandler(api_key="demo")


def test_get_time_series_intraday() -> None:
    assert handler._get_time_series_intraday(symbol="IBM", interval="5min") is not None
    assert (
        handler._get_time_series_intraday(
            symbol="IBM", interval="5min", outputsize="full"
        )
        is not None
    )
    assert (
        handler._get_time_series_intraday(
            symbol="IBM", interval="5min", month="2009-01", outputsize="full"
        )
        is not None
    )


def test_get_time_series_daily() -> None:
    assert handler._get_time_series_daily(symbol="IBM") is not None
    assert handler._get_time_series_daily(symbol="IBM", outputsize="full") is not None
    assert (
        handler._get_time_series_daily(symbol="TSCO.LON", outputsize="full") is not None
    )
    assert (
        handler._get_time_series_daily(symbol="SHOP.TRT", outputsize="full") is not None
    )
    assert (
        handler._get_time_series_daily(symbol="GPV.TRV", outputsize="full") is not None
    )
    assert (
        handler._get_time_series_daily(symbol="MBG.DEX", outputsize="full") is not None
    )
    assert (
        handler._get_time_series_daily(symbol="RELIANCE.BSE", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily(symbol="600104.SHH", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily(symbol="000002.SHZ", outputsize="full")
        is not None
    )


def test_get_time_series_daily_adjusted() -> None:
    assert handler._get_time_series_daily_adjusted(symbol="IBM") is not None
    assert (
        handler._get_time_series_daily_adjusted(symbol="IBM", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="TSCO.LON", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="SHOP.TRT", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="GPV.TRV", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="MBG.DEX", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(
            symbol="RELIANCE.BSE", outputsize="full"
        )
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="600104.SHH", outputsize="full")
        is not None
    )
    assert (
        handler._get_time_series_daily_adjusted(symbol="000002.SHZ", outputsize="full")
        is not None
    )


def test_get_time_series_weekly() -> None:
    assert handler._get_time_series_weekly(symbol="IBM") is not None
    assert handler._get_time_series_weekly(symbol="TSCO.LON") is not None


def test_get_time_series_weekly_adjusted() -> None:
    assert handler._get_time_series_weekly_adjusted(symbol="IBM") is not None
    assert handler._get_time_series_weekly_adjusted(symbol="TSCO.LON") is not None


def test_get_time_series_monthly() -> None:
    assert handler._get_time_series_monthly(symbol="IBM") is not None
    assert handler._get_time_series_monthly(symbol="TSCO.LON") is not None


def test_get_time_series_monthly_adjusted() -> None:
    assert handler._get_time_series_monthly_adjusted(symbol="IBM") is not None
    assert handler._get_time_series_monthly_adjusted(symbol="TSCO.LON") is not None


def test_get_global_quote() -> None:
    assert handler._get_global_quote(symbol="IBM") is not None
    assert handler._get_global_quote(symbol="300135.SHZ") is not None


def test_get_realtime_bulk_quotes() -> None:
    assert handler._get_realtime_bulk_quotes(symbol="MSFT,AAPL,IBM") is not None


def test_get_symbol_search() -> None:
    assert handler._get_symbol_search(keywords="tesco") is not None
    assert handler._get_symbol_search(keywords="tencent") is not None
    assert handler._get_symbol_search(keywords="BA") is not None
    assert handler._get_symbol_search(keywords="SAIC") is not None


def test_get_market_status() -> None:
    assert handler._get_market_status() is not None


def test_get_realtime_options() -> None:
    assert handler._get_realtime_options(symbol="IBM") is not None


def test_get_historical_options() -> None:
    assert handler._get_historical_options(symbol="IBM") is not None
    assert handler._get_historical_options(symbol="IBM", date="2017-11-15") is not None


def test_get_news_sentiment() -> None:
    assert handler._get_news_sentiment(tickers="AAPL") is not None
    assert (
        handler._get_news_sentiment(
            tickers="COIN,CRYPTO:BTC,FOREX:USD", time_from="20220410T0130", limit="1000"
        )
        is not None
    )


def test_get_top_gainers_losers() -> None:
    assert handler._get_top_gainers_losers() is not None


def test_get_insider_transactions() -> None:
    assert handler._get_insider_transactions(symbol="IBM") is not None


def test_get_analytics_sliding_window() -> None:
    assert (
        handler._get_analytics_sliding_window(
            SYMBOLS="AAPL,IBM",
            RANGE="2month",
            INTERVAL="DAILY",
            OHLC="close",
            WINDOW_SIZE="20",
            CALCULATIONS="MEAN,STDDEV(annualized=True)",
        )
        is not None
    )


def test_get_overview() -> None:
    assert handler._get_overview(symbol="IBM") is not None


def test_get_etf_profile() -> None:
    assert handler._get_etf_profile(symbol="QQQ") is not None


def test_get_dividends() -> None:
    assert handler._get_dividends(symbol="IBM") is not None


def test_get_splits() -> None:
    assert handler._get_splits(symbol="IBM") is not None


def test_get_income_statement() -> None:
    assert handler._get_income_statement(symbol="IBM") is not None


def test_get_balance_sheet() -> None:
    assert handler._get_balance_sheet(symbol="IBM") is not None


def test_get_cash_flow() -> None:
    assert handler._get_cash_flow(symbol="IBM") is not None


def test_get_earnings() -> None:
    assert handler._get_earnings(symbol="IBM") is not None


def test_get_fx_intraday() -> None:
    assert (
        handler._get_fx_intraday(from_symbol="EUR", to_symbol="USD", interval="5min")
        is not None
    )
    assert (
        handler._get_fx_intraday(
            from_symbol="EUR", to_symbol="USD", interval="5min", outputsize="full"
        )
        is not None
    )


def test_get_fx_daily() -> None:
    assert handler._get_fx_daily(from_symbol="EUR", to_symbol="USD") is not None
    assert (
        handler._get_fx_daily(from_symbol="EUR", to_symbol="USD", outputsize="full")
        is not None
    )


def test_get_fx_weekly() -> None:
    assert handler._get_fx_weekly(from_symbol="EUR", to_symbol="USD") is not None


def test_get_fx_monthly() -> None:
    assert handler._get_fx_monthly(from_symbol="EUR", to_symbol="USD") is not None


def test_get_crypto_intraday() -> None:
    assert (
        handler._get_crypto_intraday(symbol="ETH", market="USD", interval="5min")
        is not None
    )
    assert (
        handler._get_crypto_intraday(
            symbol="ETH", market="USD", interval="5min", outputsize="full"
        )
        is not None
    )


def test_get_digital_currency_daily() -> None:
    assert handler._get_digital_currency_daily(symbol="BTC", market="EUR") is not None


def test_get_digital_currency_weekly() -> None:
    assert handler._get_digital_currency_weekly(symbol="BTC", market="EUR") is not None


def test_get_digital_currency_monthly() -> None:
    assert handler._get_digital_currency_monthly(symbol="BTC", market="EUR") is not None


def test_get_wti() -> None:
    assert handler._get_wti(interval="monthly") is not None


def test_get_brent() -> None:
    assert handler._get_brent(interval="monthly") is not None


def test_get_natural_gas() -> None:
    assert handler._get_natural_gas(interval="monthly") is not None


def test_get_copper() -> None:
    assert handler._get_copper(interval="monthly") is not None


def test_get_aluminum() -> None:
    assert handler._get_aluminum(interval="monthly") is not None


def test_get_wheat() -> None:
    assert handler._get_wheat(interval="monthly") is not None


def test_get_corn() -> None:
    assert handler._get_corn(interval="monthly") is not None


def test_get_cotton() -> None:
    assert handler._get_cotton(interval="monthly") is not None


def test_get_sugar() -> None:
    assert handler._get_sugar(interval="monthly") is not None


def test_get_coffee() -> None:
    assert handler._get_coffee(interval="monthly") is not None


def test_get_all_commodities() -> None:
    assert handler._get_all_commodities(interval="monthly") is not None


def test_get_real_gdp() -> None:
    assert handler._get_real_gdp(interval="annual") is not None


def test_get_real_gdp_per_capita() -> None:
    assert handler._get_real_gdp_per_capita() is not None


def test_get_treasury_yield() -> None:
    assert (
        handler._get_treasury_yield(interval="monthly", maturity="10year") is not None
    )


def test_get_federal_funds_rate() -> None:
    assert handler._get_federal_funds_rate(interval="monthly") is not None


def test_get_cpi() -> None:
    assert handler._get_cpi(interval="monthly") is not None


def test_get_inflation() -> None:
    assert handler._get_inflation() is not None


def test_get_retail_sales() -> None:
    assert handler._get_retail_sales() is not None


def test_get_durables() -> None:
    assert handler._get_durables() is not None


def test_get_unemployment() -> None:
    assert handler._get_unemployment() is not None


def test_get_nonfarm_payroll() -> None:
    assert handler._get_nonfarm_payroll() is not None


def test_get_wma() -> None:
    assert (
        handler._get_wma(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_dema() -> None:
    assert (
        handler._get_dema(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_tema() -> None:
    assert (
        handler._get_tema(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_trima() -> None:
    assert (
        handler._get_trima(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_kama() -> None:
    assert (
        handler._get_kama(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_mama() -> None:
    assert (
        handler._get_mama(
            symbol="IBM", interval="daily", series_type="close", fastlimit="0.02"
        )
        is not None
    )


def test_get_vwap() -> None:
    assert handler._get_vwap(symbol="IBM", interval="15min") is not None


def test_get_t3() -> None:
    assert (
        handler._get_t3(
            symbol="IBM", interval="weekly", time_period="10", series_type="open"
        )
        is not None
    )


def test_get_macdext() -> None:
    assert (
        handler._get_macdext(symbol="IBM", interval="daily", series_type="open")
        is not None
    )


def test_get_stochf() -> None:
    assert handler._get_stochf(symbol="IBM", interval="daily") is not None


def test_get_stochrsi() -> None:
    assert (
        handler._get_stochrsi(
            symbol="IBM",
            interval="daily",
            time_period="10",
            series_type="close",
            fastkperiod="6",
            fastdmatype="1",
        )
        is not None
    )


def test_get_willr() -> None:
    assert (
        handler._get_willr(symbol="IBM", interval="daily", time_period="10") is not None
    )


def test_get_adxr() -> None:
    assert (
        handler._get_adxr(symbol="IBM", interval="daily", time_period="10") is not None
    )


def test_get_apo() -> None:
    assert (
        handler._get_apo(
            symbol="IBM",
            interval="daily",
            series_type="close",
            fastperiod="10",
            matype="1",
        )
        is not None
    )


def test_get_ppo() -> None:
    assert (
        handler._get_ppo(
            symbol="IBM",
            interval="daily",
            series_type="close",
            fastperiod="10",
            matype="1",
        )
        is not None
    )


def test_get_mom() -> None:
    assert (
        handler._get_mom(
            symbol="IBM", interval="daily", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_bop() -> None:
    assert handler._get_bop(symbol="IBM", interval="daily") is not None


def test_get_cmo() -> None:
    assert (
        handler._get_cmo(
            symbol="IBM", interval="weekly", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_roc() -> None:
    assert (
        handler._get_roc(
            symbol="IBM", interval="weekly", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_rocr() -> None:
    assert (
        handler._get_rocr(
            symbol="IBM", interval="daily", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_aroonosc() -> None:
    assert (
        handler._get_aroonosc(symbol="IBM", interval="daily", time_period="10")
        is not None
    )


def test_get_mfi() -> None:
    assert (
        handler._get_mfi(symbol="IBM", interval="weekly", time_period="10") is not None
    )


def test_get_trix() -> None:
    assert (
        handler._get_trix(
            symbol="IBM", interval="daily", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_ultosc() -> None:
    assert (
        handler._get_ultosc(symbol="IBM", interval="daily", timeperiod1="8") is not None
    )
    assert handler._get_ultosc(symbol="IBM", interval="daily") is not None


def test_get_dx() -> None:
    assert handler._get_dx(symbol="IBM", interval="daily", time_period="10") is not None


def test_get_minus_di() -> None:
    assert (
        handler._get_minus_di(symbol="IBM", interval="weekly", time_period="10")
        is not None
    )


def test_get_plus_di() -> None:
    assert (
        handler._get_plus_di(symbol="IBM", interval="daily", time_period="10")
        is not None
    )


def test_get_minus_dm() -> None:
    assert (
        handler._get_minus_dm(symbol="IBM", interval="daily", time_period="10")
        is not None
    )


def test_get_plus_dm() -> None:
    assert (
        handler._get_plus_dm(symbol="IBM", interval="daily", time_period="10")
        is not None
    )


def test_get_midpoint() -> None:
    assert (
        handler._get_midpoint(
            symbol="IBM", interval="daily", time_period="10", series_type="close"
        )
        is not None
    )


def test_get_midprice() -> None:
    assert (
        handler._get_midprice(symbol="IBM", interval="daily", time_period="10")
        is not None
    )


def test_get_sar() -> None:
    assert (
        handler._get_sar(
            symbol="IBM", interval="weekly", acceleration="0.05", maximum="0.25"
        )
        is not None
    )


def test_get_trange() -> None:
    assert handler._get_trange(symbol="IBM", interval="daily") is not None


def test_get_atr() -> None:
    assert (
        handler._get_atr(symbol="IBM", interval="daily", time_period="14") is not None
    )


def test_get_natr() -> None:
    assert (
        handler._get_natr(symbol="IBM", interval="weekly", time_period="14") is not None
    )


def test_get_ad() -> None:
    assert handler._get_ad(symbol="IBM", interval="daily") is not None


def test_get_adosc() -> None:
    assert (
        handler._get_adosc(symbol="IBM", interval="daily", fastperiod="5") is not None
    )


def test_get_obv() -> None:
    assert handler._get_obv(symbol="IBM", interval="weekly") is not None


def test_get_ht_trendline() -> None:
    assert (
        handler._get_ht_trendline(symbol="IBM", interval="daily", series_type="close")
        is not None
    )


def test_get_ht_sine() -> None:
    assert (
        handler._get_ht_sine(symbol="IBM", interval="daily", series_type="close")
        is not None
    )


def test_get_ht_trendmode() -> None:
    assert (
        handler._get_ht_trendmode(symbol="IBM", interval="weekly", series_type="close")
        is not None
    )


def test_get_ht_dcperiod() -> None:
    assert (
        handler._get_ht_dcperiod(symbol="IBM", interval="daily", series_type="close")
        is not None
    )


def test_get_ht_dcphase() -> None:
    assert (
        handler._get_ht_dcphase(symbol="IBM", interval="daily", series_type="close")
        is not None
    )


def test_get_ht_phasor() -> None:
    assert (
        handler._get_ht_phasor(symbol="IBM", interval="weekly", series_type="close")
        is not None
    )

    def get_analytics_fixed_window(self, *args, **kwargs) -> None: ...
