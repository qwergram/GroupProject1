import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Message, Company
from .historical import get_stock_history
from .moving_stocks import top_movers
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
    '''
    :: stock_movers ::
    ticker: stock ticker
    name: name of the company
    price: current price
    change: change in price since open
    pct_change: percent change since open
    volume: volume traded
    '''
    messages = list(Message.objects.filter(focus="MSFT"))
    random.shuffle(messages)
    stock_movers = top_movers()
    return render(request, 'index.html', {"streamer": messages, "stock_list": stock_movers})


def detail(request, ticker="AAPL"):
    # build the object of all the things
    '''
    :: stock_data ::
    date: datetime date of the day
    open: opening price that day
    high: high price that day
    low: low price that day
    close: closing price that day
    volume: volume traded that day
    adj_close: adjusted closing value that day
    '''
    stock_data = get_stock_history(ticker)

    company = {}
    company["message"] = "here is a message for the ticker" #Message.objects.filter(focus=ticker)
    company["ticker"] = stock_data.ticker
    company["name"] = stock_data.name
    company["price"] = stock_data.price
    company["change_dollars"] = stock_data.change
    company["change_percent"] = stock_data.pct_change

    return render(request, 'detail.html', {"company": company})


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
