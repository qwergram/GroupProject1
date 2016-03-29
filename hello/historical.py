# coding=utf-8
from __future__ import unicode_literals, print_function

from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from pylru import lrucache
import requests
from sortedcontainers import SortedDict


_PUBLIC_API_URL = "https://query.yahooapis.com/v1/public/yql"
_DATATABLES_URL = "store://datatables.org/alltableswithkeys"
_DATE_FORMAT = "%Y-%m-%d"
_MAX_FETCHED_DAYS = 365


_remembered_historical = lrucache(256)


_pool = ThreadPoolExecutor(max_workers=5)


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
    return requests.get(_PUBLIC_API_URL, params={'q': query, 'format': 'json', 'env': _DATATABLES_URL}).json()


def _yahoo_historical_range(ticker):
    query = "SELECT start, end FROM yahoo.finance.stocks WHERE symbol = '{}';".format(ticker)
    response = _yahoo_query(query)
    results = response['query']['results']['stock']
    return datetime.strptime(results['start'], _DATE_FORMAT), datetime.strptime(results['end'], _DATE_FORMAT)


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
        "SELECT * FROM yahoo.finance.historicaldata WHERE symbol = '{}' AND startDate = '{}' AND endDate = '{}'"
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
            return ticker, map(Day.from_json, response['query']['results']['quote'])
    except (KeyError, AttributeError) as ex:
        print("Problem getting historical data from Yahoo -", ex)
        return ticker, []


def fetch_stock_history(ticker, most_days=365):  # todo: nonexistent ticker case
    """
    Fetch and store the most up to date yahoo historical stock information for this stock ticker. Return nothing.

    If more than a certain number of stock histories are requested, the least recently used will be forgotten.
    """
    start, end = _yahoo_historical_range(ticker)
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
        for day in _remembered_historical[ticker].irange(start_date, end_date):
            results.append(day)
    return results
