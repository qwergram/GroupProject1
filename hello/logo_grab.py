import requests
from bs4 import BeautifulSoup

YAHOO_ENDPOINT = "http://finance.yahoo.com/q/pr?s={}"

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

if __name__ == "__main__":
    target = get_endpoint("MSFT")
    response = get_response(target)
    soup = handle_response(response)
    import pdb; pdb.set_trace()
