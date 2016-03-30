# coding=utf-8
from __future__ import unicode_literals

from datetime import datetime, timedelta
from functools import namedtuple

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException


YAHOO_MOVERS_URL = "http://finance.yahoo.com/_remote/?m_id=MediaRemoteInstance&instance_id=85ac7b2b-640f-323f-a1c1" \
                   "-00b2f4865d18&mode=xhr&ctab=tab1&nolz=1&count=20&start=0&category=mostactive&no_tabs=1"
GOOGLE_MOVERS_URL = "https://www.google.com/finance"


_yahoo_cached = None
_google_cached = None
CACHE_TIME = timedelta(minutes=5)


class TopMover(namedtuple('TopMover', "ticker name price change pct_change volume")):
    pass


def _yahoo_top_movers(data):
    global _yahoo_cached
    now = datetime.utcnow()
    if _yahoo_cached and (_yahoo_cached[0] + CACHE_TIME <= now):
        return _yahoo_cached[1]

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
    _yahoo_cached = now, results
    # TODO: prefetch historical data for these stocks
    return results


def _google_top_movers():
    raise NotImplemented  # TODO this


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
    try:
        return _yahoo_top_movers(requests.get(YAHOO_MOVERS_URL).text)
    except RequestException as ex:
        print("Problem getting yahoo movers data:", ex)
        return []
