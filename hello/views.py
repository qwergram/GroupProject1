# coding=utf-8
import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Message, Company
from .stock_info import get_current_quote, top_movers
from .stocktwits import get_stock_comments, format_into_table, save_message
from .twitter_api import get_twitter_comments, json_into_table
from .reddit import (
    get_companies,
    ticker_to_name,
    save_reddit_articles,
    scrape_reddit
)


def ajax_load(request):
    return render(request, 'loading.html')

def index(request):
    """
    :: stock_movers ::
    ticker: stock ticker
    name: name of the company
    price: current price
    change: change in price since open
    pct_change: percent change since open
    volume: volume traded
    """
    # XXX messages should be a list of messages of the biggest movers
    messages = list(Message.objects.filter(focus="MSFT"))
    random.shuffle(messages)
    stock_movers = top_movers()
    return render(request, 'index.html', {"streamer": messages, "stock_list": stock_movers})


def detail(request, ticker="MSFT"):

    stock_detail = get_current_quote(ticker)
    company = Message.objects.filter(focus=ticker)
    return render(request, 'detail.html', {"company": company, "stock": stock_detail})


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
