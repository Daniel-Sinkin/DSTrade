from src.av_integration_api import AlphaVantageAPIHandler

api_handler = AlphaVantageAPIHandler(api_key="demo")


# fmt: off
def test_get_time_series_intraday() -> None:
    assert api_handler.get_time_series_intraday(symbol="IBM", interval="5min") is not None
    assert api_handler.get_time_series_intraday(symbol="IBM", interval="5min", outputsize="full") is not None
    assert api_handler.get_time_series_intraday(symbol="IBM", interval="5min", month="2009-01", outputsize="full") is not None

def test_get_time_series_daily() -> None:
    assert api_handler.get_time_series_daily(symbol="IBM") is not None
    assert api_handler.get_time_series_daily(symbol="IBM", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="TSCO.LON", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="SHOP.TRT", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="GPV.TRV", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="MBG.DEX", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="RELIANCE.BSE", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="600104.SHH", outputsize="full") is not None
    assert api_handler.get_time_series_daily(symbol="000002.SHZ", outputsize="full") is not None

def test_get_time_series_daily_adjusted() -> None:
    assert api_handler.get_time_series_daily_adjusted(symbol="IBM") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="IBM", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="TSCO.LON", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="SHOP.TRT", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="GPV.TRV", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="MBG.DEX", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="RELIANCE.BSE", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="600104.SHH", outputsize="full") is not None
    assert api_handler.get_time_series_daily_adjusted(symbol="000002.SHZ", outputsize="full") is not None

def test_get_time_series_weekly() -> None:
    assert api_handler.get_time_series_weekly(symbol="IBM") is not None
    assert api_handler.get_time_series_weekly(symbol="TSCO.LON") is not None

def test_get_time_series_weekly_adjusted() -> None:
    assert api_handler.get_time_series_weekly_adjusted(symbol="IBM") is not None
    assert api_handler.get_time_series_weekly_adjusted(symbol="TSCO.LON") is not None

def test_get_time_series_monthly() -> None:
    assert api_handler.get_time_series_monthly(symbol="IBM") is not None
    assert api_handler.get_time_series_monthly(symbol="TSCO.LON") is not None

def test_get_time_series_monthly_adjusted() -> None:
    assert api_handler.get_time_series_monthly_adjusted(symbol="IBM") is not None
    assert api_handler.get_time_series_monthly_adjusted(symbol="TSCO.LON") is not None

def test_get_global_quote() -> None:
    assert api_handler.get_global_quote(symbol="IBM") is not None
    assert api_handler.get_global_quote(symbol="300135.SHZ") is not None

def test_get_realtime_bulk_quotes() -> None:
    assert api_handler.get_realtime_bulk_quotes(symbol="MSFT,AAPL,IBM") is not None

def test_get_symbol_search() -> None:
    assert api_handler.get_symbol_search(keywords="tesco") is not None
    assert api_handler.get_symbol_search(keywords="tencent") is not None
    assert api_handler.get_symbol_search(keywords="BA") is not None
    assert api_handler.get_symbol_search(keywords="SAIC") is not None

def test_get_market_status() -> None:
    assert api_handler.get_market_status() is not None

def test_get_realtime_options() -> None:
    assert api_handler.get_realtime_options(symbol="IBM") is not None

def test_get_historical_options() -> None:
    assert api_handler.get_historical_options(symbol="IBM") is not None
    assert api_handler.get_historical_options(symbol="IBM", date="2017-11-15") is not None

def test_get_news_sentiment() -> None:
    assert api_handler.get_news_sentiment(tickers="AAPL") is not None
    assert api_handler.get_news_sentiment(tickers="COIN,CRYPTO:BTC,FOREX:USD", time_from="20220410T0130", limit="1000") is not None

def test_get_top_gainers_losers() -> None:
    assert api_handler.get_top_gainers_losers() is not None

def test_get_insider_transactions() -> None:
    assert api_handler.get_insider_transactions(symbol="IBM") is not None

def test_get_analytics_sliding_window() -> None:
    assert api_handler.get_analytics_sliding_window(SYMBOLS="AAPL,IBM", RANGE="2month", INTERVAL="DAILY", OHLC="close", WINDOW_SIZE="20", CALCULATIONS="MEAN,STDDEV(annualized=True)") is not None

def test_get_overview() -> None:
    assert api_handler.get_overview(symbol="IBM") is not None

def test_get_etf_profile() -> None:
    assert api_handler.get_etf_profile(symbol="QQQ") is not None

def test_get_dividends() -> None:
    assert api_handler.get_dividends(symbol="IBM") is not None

def test_get_splits() -> None:
    assert api_handler.get_splits(symbol="IBM") is not None

def test_get_income_statement() -> None:
    assert api_handler.get_income_statement(symbol="IBM") is not None

def test_get_balance_sheet() -> None:
    assert api_handler.get_balance_sheet(symbol="IBM") is not None

def test_get_cash_flow() -> None:
    assert api_handler.get_cash_flow(symbol="IBM") is not None

def test_get_earnings() -> None:
    assert api_handler.get_earnings(symbol="IBM") is not None

def test_get_fx_intraday() -> None:
    assert api_handler.get_fx_intraday(from_symbol="EUR", to_symbol="USD", interval="5min") is not None
    assert api_handler.get_fx_intraday(from_symbol="EUR", to_symbol="USD", interval="5min", outputsize="full") is not None

def test_get_fx_daily() -> None:
    assert api_handler.get_fx_daily(from_symbol="EUR", to_symbol="USD") is not None
    assert api_handler.get_fx_daily(from_symbol="EUR", to_symbol="USD", outputsize="full") is not None

def test_get_fx_weekly() -> None:
    assert api_handler.get_fx_weekly(from_symbol="EUR", to_symbol="USD") is not None

def test_get_fx_monthly() -> None:
    assert api_handler.get_fx_monthly(from_symbol="EUR", to_symbol="USD") is not None

def test_get_crypto_intraday() -> None:
    assert api_handler.get_crypto_intraday(symbol="ETH", market="USD", interval="5min") is not None
    assert api_handler.get_crypto_intraday(symbol="ETH", market="USD", interval="5min", outputsize="full") is not None

def test_get_digital_currency_daily() -> None:
    assert api_handler.get_digital_currency_daily(symbol="BTC", market="EUR") is not None

def test_get_digital_currency_weekly() -> None:
    assert api_handler.get_digital_currency_weekly(symbol="BTC", market="EUR") is not None

def test_get_digital_currency_monthly() -> None:
    assert api_handler.get_digital_currency_monthly(symbol="BTC", market="EUR") is not None

def test_get_wti() -> None:
    assert api_handler.get_wti(interval="monthly") is not None

def test_get_brent() -> None:
    assert api_handler.get_brent(interval="monthly") is not None

def test_get_natural_gas() -> None:
    assert api_handler.get_natural_gas(interval="monthly") is not None

def test_get_copper() -> None:
    assert api_handler.get_copper(interval="monthly") is not None

def test_get_aluminum() -> None:
    assert api_handler.get_aluminum(interval="monthly") is not None

def test_get_wheat() -> None:
    assert api_handler.get_wheat(interval="monthly") is not None

def test_get_corn() -> None:
    assert api_handler.get_corn(interval="monthly") is not None

def test_get_cotton() -> None:
    assert api_handler.get_cotton(interval="monthly") is not None

def test_get_sugar() -> None:
    assert api_handler.get_sugar(interval="monthly") is not None

def test_get_coffee() -> None:
    assert api_handler.get_coffee(interval="monthly") is not None

def test_get_all_commodities() -> None:
    assert api_handler.get_all_commodities(interval="monthly") is not None

def test_get_real_gdp() -> None:
    assert api_handler.get_real_gdp(interval="annual") is not None

def test_get_real_gdp_per_capita() -> None:
    assert api_handler.get_real_gdp_per_capita() is not None

def test_get_treasury_yield() -> None:
    assert api_handler.get_treasury_yield(interval="monthly", maturity="10year") is not None

def test_get_federal_funds_rate() -> None:
    assert api_handler.get_federal_funds_rate(interval="monthly") is not None

def test_get_cpi() -> None:
    assert api_handler.get_cpi(interval="monthly") is not None

def test_get_inflation() -> None:
    assert api_handler.get_inflation() is not None

def test_get_retail_sales() -> None:
    assert api_handler.get_retail_sales() is not None

def test_get_durables() -> None:
    assert api_handler.get_durables() is not None

def test_get_unemployment() -> None:
    assert api_handler.get_unemployment() is not None

def test_get_nonfarm_payroll() -> None:
    assert api_handler.get_nonfarm_payroll() is not None

def test_get_wma() -> None:
    assert api_handler.get_wma(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_dema() -> None:
    assert api_handler.get_dema(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_tema() -> None:
    assert api_handler.get_tema(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_trima() -> None:
    assert api_handler.get_trima(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_kama() -> None:
    assert api_handler.get_kama(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_mama() -> None:
    assert api_handler.get_mama(symbol="IBM", interval="daily", series_type="close", fastlimit="0.02") is not None

def test_get_vwap() -> None:
    assert api_handler.get_vwap(symbol="IBM", interval="15min") is not None

def test_get_t3() -> None:
    assert api_handler.get_t3(symbol="IBM", interval="weekly", time_period="10", series_type="open") is not None

def test_get_macdext() -> None:
    assert api_handler.get_macdext(symbol="IBM", interval="daily", series_type="open") is not None

def test_get_stochf() -> None:
    assert api_handler.get_stochf(symbol="IBM", interval="daily") is not None

def test_get_stochrsi() -> None:
    assert api_handler.get_stochrsi(symbol="IBM", interval="daily", time_period="10", series_type="close", fastkperiod="6", fastdmatype="1") is not None

def test_get_willr() -> None:
    assert api_handler.get_willr(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_adxr() -> None:
    assert api_handler.get_adxr(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_apo() -> None:
    assert api_handler.get_apo(symbol="IBM", interval="daily", series_type="close", fastperiod="10", matype="1") is not None

def test_get_ppo() -> None:
    assert api_handler.get_ppo(symbol="IBM", interval="daily", series_type="close", fastperiod="10", matype="1") is not None

def test_get_mom() -> None:
    assert api_handler.get_mom(symbol="IBM", interval="daily", time_period="10", series_type="close") is not None

def test_get_bop() -> None:
    assert api_handler.get_bop(symbol="IBM", interval="daily") is not None

def test_get_cmo() -> None:
    assert api_handler.get_cmo(symbol="IBM", interval="weekly", time_period="10", series_type="close") is not None

def test_get_roc() -> None:
    assert api_handler.get_roc(symbol="IBM", interval="weekly", time_period="10", series_type="close") is not None

def test_get_rocr() -> None:
    assert api_handler.get_rocr(symbol="IBM", interval="daily", time_period="10", series_type="close") is not None

def test_get_aroonosc() -> None:
    assert api_handler.get_aroonosc(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_mfi() -> None:
    assert api_handler.get_mfi(symbol="IBM", interval="weekly", time_period="10") is not None

def test_get_trix() -> None:
    assert api_handler.get_trix(symbol="IBM", interval="daily", time_period="10", series_type="close") is not None

def test_get_ultosc() -> None:
    assert api_handler.get_ultosc(symbol="IBM", interval="daily", timeperiod1="8") is not None
    assert api_handler.get_ultosc(symbol="IBM", interval="daily") is not None

def test_get_dx() -> None:
    assert api_handler.get_dx(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_minus_di() -> None:
    assert api_handler.get_minus_di(symbol="IBM", interval="weekly", time_period="10") is not None

def test_get_plus_di() -> None:
    assert api_handler.get_plus_di(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_minus_dm() -> None:
    assert api_handler.get_minus_dm(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_plus_dm() -> None:
    assert api_handler.get_plus_dm(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_midpoint() -> None:
    assert api_handler.get_midpoint(symbol="IBM", interval="daily", time_period="10", series_type="close") is not None

def test_get_midprice() -> None:
    assert api_handler.get_midprice(symbol="IBM", interval="daily", time_period="10") is not None

def test_get_sar() -> None:
    assert api_handler.get_sar(symbol="IBM", interval="weekly", acceleration="0.05", maximum="0.25") is not None

def test_get_trange() -> None:
    assert api_handler.get_trange(symbol="IBM", interval="daily") is not None

def test_get_atr() -> None:
    assert api_handler.get_atr(symbol="IBM", interval="daily", time_period="14") is not None

def test_get_natr() -> None:
    assert api_handler.get_natr(symbol="IBM", interval="weekly", time_period="14") is not None

def test_get_ad() -> None:
    assert api_handler.get_ad(symbol="IBM", interval="daily") is not None

def test_get_adosc() -> None:
    assert api_handler.get_adosc(symbol="IBM", interval="daily", fastperiod="5") is not None

def test_get_obv() -> None:
    assert api_handler.get_obv(symbol="IBM", interval="weekly") is not None

def test_get_ht_trendline() -> None:
    assert api_handler.get_ht_trendline(symbol="IBM", interval="daily", series_type="close") is not None

def test_get_ht_sine() -> None:
    assert api_handler.get_ht_sine(symbol="IBM", interval="daily", series_type="close") is not None

def test_get_ht_trendmode() -> None:
    assert api_handler.get_ht_trendmode(symbol="IBM", interval="weekly", series_type="close") is not None

def test_get_ht_dcperiod() -> None:
    assert api_handler.get_ht_dcperiod(symbol="IBM", interval="daily", series_type="close") is not None

def test_get_ht_dcphase() -> None:
    assert api_handler.get_ht_dcphase(symbol="IBM", interval="daily", series_type="close") is not None

def test_get_ht_phasor() -> None:
    assert api_handler.get_ht_phasor(symbol="IBM", interval="weekly", series_type="close") is not None

def get_analytics_fixed_window(self, *args, **kwargs) -> None: ... # This api function is currently not supported
# fmt: off
