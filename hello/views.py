from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Message, Company
import random

from .stocktwits import get_stock_comments, format_into_table, save_message
from .twitter_api import get_twitter_comments, json_into_table
from .reddit import (
    get_companies,
    ticker_to_name,
    save_reddit_articles,
    scrape_reddit
)


def index(request):
    # XXX messages should be a list of messages of the biggest movers
    messages = list(Message.objects.filter(focus="MSFT"))
    random.shuffle(messages)
    return render(request, 'index.html', {"streamer": messages})


def detail(request, ticker=None):
    stock_list = Message.objects.filter(focus=ticker)
    return render(request, 'detail.html', stock_list)


def test(request, ticker):
    ticker = ticker.upper()
    messages = get_stock_comments(ticker)
    for index, message in enumerate(messages):
        message = format_into_table(message, ticker)
        messages[index] = message
        save_message(message)
    try:
        companies = get_companies()
        query = ticker_to_name(companies, ticker)
        reddit_messages = scrape_reddit(ticker, query)
        save_reddit_articles(reddit_messages)
    except KeyError:
        reddit_messages = []

    tweets = get_twitter_comments(ticker)
    for index, message in enumerate(tweets):
        message = json_into_table(message, ticker)
        tweets[index] = message

    return JsonResponse(messages + reddit_messages + tweets, safe=False)



