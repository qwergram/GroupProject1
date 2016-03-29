import json
import io
import requests

REDDIT_API_ENDPOINT = "https://api.reddit.com/search?q={}&type=link"


def get_companies():
    # XXX Search the stocks database in the future
    with io.open("stocktalk/static/raw_data/symbols_usa_only.json") as f:
        j = f.read()
    list_of_companies = json.loads(j)
    dict_of_companies = {}
    for company in list_of_companies:
        dict_of_companies[company['Ticker']] = company
    return dict_of_companies


def ticker_to_name(data, ticker):
    if not isinstance(data, dict):
        raise ValueError("Invalid company data")
    if not isinstance(ticker, str):
        raise ValueError("Invalid ticker")
    company_data = data.get(ticker)
    if company_data:
        return company_data["Name"]
    raise ValueError("Ticker not found")


def scrape_reddit(query):
    query = query.replace(' ', '+')
    response = requests.get(REDDIT_API_ENDPOINT.format(query),
                            headers={"User-Agent": "StockTalk @ https://github.com/qwergram/GroupProject1"})
    if not response.ok:
        raise ConnectionError("Reddit didn't like the query, try again later")
    json_blob = response.json()['data']['children']
    links = []
    for post in json_blob:
        link = post['data']['url']
        date = post['data']['created_utc']
        if "reddit.com" not in link:
            links.append(link)
    return links
