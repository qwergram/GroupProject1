# coding=utf-8
import requests
from hello.models import Message
from django.db.utils import IntegrityError
try:
    from html import unescape
except ImportError:  # I hate python2
    from HTMLParser import HTMLParser

    def unescape(*args, **kwargs):
        return HTMLParser().unescape(*args, **kwargs)

API_ENDPOINT = "https://api.stocktwits.com/api/2/streams/symbol/{}.json"


def get_stock_comments(ticker):
    resp = requests.get(API_ENDPOINT.format(ticker))
    if resp.status_code != 200:
        raise ValueError("Stock not found")
    json = resp.json()
    return json.get('messages')


def format_into_table(message, ticker):
    try:
        ticker = str(ticker.decode())
    except AttributeError:
        pass
    if not isinstance(ticker, str):
        raise ValueError("Invalid ticker!")
    try:
        hashtags = []
        if "#" in message['body']:
            words = message['body'].split()
            for word in words:
                if word.startswith('#') and word[1:].replace(',', '').isalnum():
                    hashtags.append(word)
        to_return = {
            "social_id": str(message['id']),
            "source": "stocktwits",
            "focus": ticker,
            "popularity": message['reshares']['reshared_count'],
            "author": message['user']['username'],
            "author_image": message['user']['avatar_url_ssl'],
            "created_time": message['created_at'],
            "content": unescape(message['body']),
            "hashtags": hashtags,
            "symbols": [stock['symbol'] for stock in message['symbols']],
            "urls": [link['url'] for link in message.get('links', [])],
            "url": "http://stocktwits.com/{}/message/{}".format(message['user']['username'], str(message['id']))
        }
        return to_return
    except (TypeError, KeyError):
        raise ValueError("Invalid message!")


def save_message(message):
    try:
        Message(**message).save()
        return True
    except IntegrityError:
        return False
