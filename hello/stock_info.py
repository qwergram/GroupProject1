# coding=utf-8
from __future__ import unicode_literals, print_function
from concurrent.futures import ThreadPoolExecutor

from datetime import timedelta, datetime
from bs4 import BeautifulSoup
from collections import namedtuple
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from pylru import lrucache
import requests
from requests import RequestException
from sortedcontainers import SortedDict


CACHE_TIME = timedelta(minutes=5)
_pool = ThreadPoolExecutor(max_workers=5)

# web scraping
_PUBLIC_API_URL = "https://query.yahooapis.com/v1/public/yql"
_YAHOO_MOVERS_URL = "http://finance.yahoo.com/_remote/?m_id=MediaRemoteInstance&instance_id=85ac7b2b-640f-323f-a1c1" \
                   "-00b2f4865d18&mode=xhr&ctab=tab1&nolz=1&count=20&start=0&category=mostactive&no_tabs=1"
_GOOGLE_MOVERS_URL = "https://www.google.com/finance"
_yahoo_cached = None
_google_cached = None
_quotes_cache = lrucache(256)

# yahoo api and historical caching
_DATATABLES_URL = "store://datatables.org/alltableswithkeys"
_DATE_FORMAT = "%Y-%m-%d"
_MAX_FETCHED_DAYS = 365
_remembered_historical = lrucache(256)


class TopMover(namedtuple('TopMover', "ticker name price change pct_change volume")):
    pass


def _yahoo_top_movers(data):
    results = []
    soup = BeautifulSoup(data, 'html5lib')
    for stock in soup.tbody.findAll('tr'):
        results.append(TopMover(
            ticker=stock.find('td', {'class': "symbol"}).a.text,
            name=stock.find('td', {'class': "name"}).a.text,
            price=float(stock.find('td', {'class': "price"}).span.text),
            change=float(stock.find('td', {'class': "change"}).span.text),
            pct_change=float(stock.find('td', {'class': "pct-change"}).span.text.rstrip("%")),
            volume=int(stock.find('td', {'class': "volume"}).span.text.replace(",", "")),
        ))
    # TODO: prefetch historical data for these stocks
    return results


# def _google_top_movers():
#     raise NotImplemented  # TODO this


def top_movers():
    """
    Return the top movers in the current stock market.

    Each one has the following attributes:

    ticker: stock ticker
    name: name of the company
    price: current price
    change: change in price since open
    pct_change: percent change since open
    volume: volume traded
    """
    global _yahoo_cached
    now = datetime.utcnow()
    if _yahoo_cached and (_yahoo_cached[0] + CACHE_TIME >= now):
        return _yahoo_cached[1]

    try:
        results = _yahoo_top_movers(requests.get(_YAHOO_MOVERS_URL).text)
        _yahoo_cached = now, results
        return results
    except RequestException as ex:
        print("Problem getting yahoo movers data:", ex)
        return []


class Day(namedtuple("Day", "date open high low close volume adj_close")):
    @classmethod
    def from_json(cls, day_data):
        try:
            return cls(
                datetime.strptime(day_data['Date'], _DATE_FORMAT),
                day_data['Open'],
                day_data['High'],
                day_data['Low'],
                day_data['Close'],
                day_data['Volume'],
                day_data['Adj_Close']
            )
        except (KeyError, ValueError):
            return None


def _latest_remembered_entry(ticker):
    ticker = ticker.lower()
    if ticker in _remembered_historical:
        days = _remembered_historical[ticker.lower()]
        last_day = next(reversed(days), None)
        return last_day
    else:  # ticker not cached
        return None


def _remember_day(ticker, day):
    ticker = ticker.lower()
    # setdefault the history for this ticker
    if ticker not in _remembered_historical:
        ticker_history = SortedDict()
        _remembered_historical[ticker] = ticker_history
    else:
        ticker_history = _remembered_historical[ticker]

    ticker_history[day.date] = day


def _yahoo_query(query):
    # print("QUERY", query)
    try:
        return requests.get(_PUBLIC_API_URL, params={'q': query, 'format': 'json', 'env': _DATATABLES_URL}).json()
    except (RequestException, JSONDecodeError):
        return {}


def _yahoo_historical_range(ticker):
    query = "SELECT start, end FROM yahoo.finance.stocks WHERE symbol = '{0}';".format(ticker)
    response = _yahoo_query(query)
    try:
        results = response['query']['results']['stock']
        return datetime.strptime(results['start'], _DATE_FORMAT), datetime.strptime(results['end'], _DATE_FORMAT)
    except (KeyError, TypeError):
        return None


def _break_up_fetch_range(start, end):
    """break up a longer range of time into shorter start and end date ranges to fetch from the api"""
    while True:
        range_end = start + timedelta(days=_MAX_FETCHED_DAYS - 1)
        if range_end >= end:
            if start <= end:
                yield start, end
            return
        yield start, range_end
        start += timedelta(days=_MAX_FETCHED_DAYS)


def _fetch_yahoo_historical(params):
    """Fetch historical data from the yahoo api"""
    ticker, start, end = params
    query = (
        "SELECT * FROM yahoo.finance.historicaldata WHERE symbol = '{0}' AND startDate = '{1}' AND endDate = '{2}'"
        .format(
            ticker,
            start.strftime(_DATE_FORMAT),
            end.strftime(_DATE_FORMAT),
        )
    )
    response = _yahoo_query(query)
    try:
        if response['query']['count'] == 0:  # TODO: error cases for missing keys etc.
            return ticker, []
        elif response['query']['count'] == 1:
            # single responses aren't wrapped in a list ¯\_(ツ)_/¯
            return ticker, [Day.from_json(response['query']['results']['quote'])]
        else:
            return ticker, list(map(Day.from_json, response['query']['results']['quote']))
    except (KeyError, TypeError) as ex:
        print("Problem getting historical data from Yahoo -", ex)
        return ticker, []


def fetch_stock_history(ticker, most_days=365):  # todo: nonexistent ticker case
    """
    Fetch and store the most up to date yahoo historical stock information for this stock ticker. Return nothing.

    If more than a certain number of stock histories are requested, the least recently used will be forgotten.
    """
    try:
        start, end = _yahoo_historical_range(ticker)
    except (RequestException, JSONDecodeError, ValueError, TypeError):
        return
    start = max(start, end - timedelta(days=most_days - 1))
    most_recent_stored_date = _latest_remembered_entry(ticker)
    fetch_start = most_recent_stored_date + timedelta(days=1) if most_recent_stored_date else start
    api_data = _pool.map(
        _fetch_yahoo_historical,
        ((ticker, range_start, range_end) for range_start, range_end in _break_up_fetch_range(
            fetch_start, end
        ))
    )
    for ticker, days in api_data:
        for day in days:
            if day:
                _remember_day(ticker, day)


def get_stock_history(ticker, start_date=None, end_date=None):
    """
    Return a list of Day namedtuples with stock information about all the currently stored data for this stock ticker
    in the given (inclusive) date range.

    The resulting value is a list of Day objects with the following attributes:
    date: datetime date of the day
    open: opening price that day
    high: high price that day
    low: low price that day
    close: closing price that day
    volume: volume traded that day
    adj_close: adjusted closing value that day
    """
    results = []
    ticker = ticker.lower()

    # default to finding the last year of results
    if end_date is None:
        end_date = _latest_remembered_entry(ticker) or datetime.utcnow().date()
    if start_date is None:
        start_date = end_date - timedelta(days=364)

    if ticker in _remembered_historical:
        for day_date in _remembered_historical[ticker].irange(start_date, end_date):
            results.append(_remembered_historical[ticker][day_date])
    return results


def _fetch_current_quote(ticker):
    """Fetch quote info from yahoo"""
    try:
        result = _yahoo_query("SELECT * FROM yahoo.finance.quotes WHERE symbol = '{0}'".format(ticker))
        quote = result['query']['results']['quote']
        return quote if quote['Name'] else {}  # nonexistent tickers return None for every value
    except (KeyError, TypeError):
        return {}


def get_current_quote(ticker):
    """
    Return current stock quote information for the given stock ticker or, if something goes wrong or the ticker does
    not exist, an empty dict. Cached in memory.

    The return value is a dictionary that most likely has the following exact keys:
    [*] = using this value in detail

    AfterHoursChangeRealtime
    AnnualizedGain
    Ask
    AskRealtime
    AverageDailyVolume
    Bid            [*]
    BidRealtime
    BookValue
    Change         [*]
    ChangeFromFiftydayMovingAverage
    ChangeFromTwoHundreddayMovingAverage
    ChangeFromYearHigh
    ChangeFromYearLow
    ChangePercentRealtime
    ChangeRealtime
    Change_PercentChange
    ChangeinPercent
    Commission
    Currency
    DaysHigh
    DaysLow
    DaysRange
    DaysRangeRealtime
    DaysValueChange
    DaysValueChangeRealtime
    DividendPayDate
    DividendShare
    DividendYield
    EBITDA
    EPSEstimateCurrentYear
    EPSEstimateNextQuarter
    EPSEstimateNextYear
    EarningsShare
    ErrorIndicationreturnedforsymbolchangedinvalid
    ExDividendDate
    FiftydayMovingAverage
    HighLimit
    HoldingsGain
    HoldingsGainPercent
    HoldingsGainPercentRealtime
    HoldingsGainRealtime
    HoldingsValue
    HoldingsValueRealtime
    LastTradeDate
    LastTradePriceOnly
    LastTradeRealtimeWithTime
    LastTradeTime
    LastTradeWithTime
    LowLimit
    MarketCapRealtime
    MarketCapitalization
    MoreInfo
    Name            [*]
    Notes
    OneyrTargetPrice
    Open
    OrderBookRealtime
    PEGRatio
    PERatio
    PERatioRealtime
    PercebtChangeFromYearHigh
    PercentChange  [*]
    PercentChangeFromFiftydayMovingAverage
    PercentChangeFromTwoHundreddayMovingAverage
    PercentChangeFromYearLow
    PreviousClose
    PriceBook
    PriceEPSEstimateCurrentYear
    PriceEPSEstimateNextYear
    PricePaid
    PriceSales
    SharesOwned
    ShortRatio
    StockExchange
    Symbol        [*]
    symbol
    TickerTrend
    TradeDate
    TwoHundreddayMovingAverage
    Volume
    YearHigh
    YearLow
    YearRange
    """
    ticker = ticker.lower()
    now = datetime.utcnow()
    if ticker in _quotes_cache:
        cached_time, data = _quotes_cache[ticker]
        if cached_time + CACHE_TIME >= now:
            return data
    data = _fetch_current_quote(ticker)
    _quotes_cache[ticker] = now, data
    return data
