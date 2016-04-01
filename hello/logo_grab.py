import requests
from bs4 import BeautifulSoup
try:
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import urlparse
    urlparse = urlparse.urlparse

try:
    ConnectionError
except NameError:
    ConnectionError = ValueError

YAHOO_ENDPOINT = "http://finance.yahoo.com/q/pr?s={}"
CLEARBIT_ENDPOINT = "https://logo.clearbit.com/{}?format=png&size=438"

def get_endpoint(ticker):
    return YAHOO_ENDPOINT.format(ticker).lower()


def get_response(target):
    return requests.get(target)


def handle_response(response):
    if not response.ok:
        raise ConnectionError("Yahoo didn't like that")
    soup = BeautifulSoup(response.text, "html5lib")
    pool = []
    for anchor in soup.find_all("a", href=True):
        link = anchor['href'].lower()
        if link.startswith("http://") or link.startswith("https://"):
            if link in pool:
                return link
            if "yahoo" not in link:
                pool.append(link)
    raise ValueError("Invalid Ticker")

def get_domain(url):
    return urlparse(url).netloc


def get_logo(domain):
    return CLEARBIT_ENDPOINT.format(domain)


def main(ticker):
    target = get_endpoint(ticker)
    response = get_response(target)
    url = handle_response(response)
    domain = get_domain(url)
    return get_logo(domain)
