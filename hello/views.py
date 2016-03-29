from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .stocktwits import get_stock_comments, format_into_table, save_message
from .reddit import (
    get_companies,
    ticker_to_name,
    save_reddit_articles,
    scrape_reddit
)


def index(request):
    return render(request, 'index.html')


def test(request, ticker):
    ticker = ticker.upper()
    messages = get_stock_comments(ticker)
    for index, message in enumerate(messages):
        message = format_into_table(message, ticker)
        messages[index] = message
        save_message(message)
    try:
        import pdb; pdb.set_trace()

        companies = get_companies()
        query = ticker_to_name(companies, ticker)
        reddit_messages = scrape_reddit(ticker, query)
        save_reddit_articles(reddit_messages)
    except KeyError:
        reddit_messages = []
    return JsonResponse(messages + reddit_messages, safe=False)


def detail(request):
    return render(request, 'detail.html')
