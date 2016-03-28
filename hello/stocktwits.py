import requests

API_ENDPOINT = "https://api.stocktwits.com/api/2/streams/symbol/{}.json"


def get_stock_comments(ticker):
    resp = requests.get(API_ENDPOINT.format(ticker))
    if resp.status_code != 200:
        raise ValueError("Stock not found")
    json = resp.json()
    return json.get('messages')


if __name__ == "__main__":
    get_stock_comments("MSFT")
