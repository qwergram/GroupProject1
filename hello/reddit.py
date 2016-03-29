import json
import io
import requests
from html import unescape
from hello.models import Message
from django.db.utils import IntegrityError

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


def save_reddit_article(messages):
    for link in messages:
        try:
            Message(**link).save()
            return True
        except IntegrityError:
            return False


def scrape_reddit(ticker, query):
    query = query.replace(' ', '+')
    response = requests.get(REDDIT_API_ENDPOINT.format(query),
                            headers={"User-Agent": "StockTalk @ https://github.com/qwergram/GroupProject1"})
    if not response.ok:
        raise ConnectionError("Reddit didn't like the query, try again later")
    json_blob = response.json()['data']['children']
    links = []
    for post in json_blob:
        if "reddit.com" not in post['data']['permalink']:
            template = {
                "social_id": post['data']['id'],
                "source": "reddit",
                "focus": ticker,
                "popularity": post['data']['ups'],
                "author": post['data']['author'],
                "author_image": "https://www.redditstatic.com/icon-touch.png",
                "created_time": post['data']['created_utc'],
                "content": post['data']['title'],
                "symbols": [ticker],
                "urls": [post['data']['url']],
                "url": "http://www.reddit.com{}".format(post['data']['permalink'])
            }
            links.append(template)

    return links
