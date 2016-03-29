import json
import io


def get_companies():
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
