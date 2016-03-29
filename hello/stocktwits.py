import requests
from hello.models import Message
from django.db.utils import IntegrityError

API_ENDPOINT = "https://api.stocktwits.com/api/2/streams/symbol/{}.json"


def get_stock_comments(ticker):
    resp = requests.get(API_ENDPOINT.format(ticker))
    if resp.status_code != 200:
        raise ValueError("Stock not found")
    json = resp.json()
    return json.get('messages')


def format_into_table(message, ticker):
    if not isinstance(ticker, str):
        raise ValueError("Invalid ticker!")
    try:
        to_return = {
            "social_id": str(message['id']),
            "source": "stocktwits",
            "focus": ticker,
            "popularity": message['reshares']['reshared_count'],
            "author": message['user']['username'],
            "author_image": message['user']['avatar_url_ssl'],
            "created_time": message['created_at'],
            "content": message['body'],
            "symbols": [stock['symbol'] for stock in message['symbols']],
            "urls": message.get('links', '[]'),
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


if __name__ == "__main__":
    ticker = "MSFT"
    messages = get_stock_comments(ticker)
    for index, message in enumerate(messages):
        message = format_into_table(message, ticker)
        save_message(message)
