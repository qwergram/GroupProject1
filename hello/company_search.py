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
