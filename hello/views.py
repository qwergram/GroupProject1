# coding=utf-8
import random
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
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
    Requests the biggest movers then looks up the current data
    for those movers for a given index.
    """
    # Get biggest movers
    movers = top_movers()

    # Get latest data
    stock_mover_quotes = {}
    for stock in movers:
        stock_mover_quotes[stock.ticker] = get_current_quote(stock.ticker)

    # XXX messages should be a list of messages of the biggest movers
    messages = list(Message.objects.filter(source="twitter"))[:33]
    messages += list(Message.objects.filter(source="stocktwits"))[:33]
    messages += list(Message.objects.filter(source="reddit"))[:33]
    random.shuffle(messages)

    return render(
        request,
        'index.html',
        {"streamer": messages, "stock_list": stock_mover_quotes.values()}
    )


def detail(request, ticker="MSFT"):
    stock_detail = get_current_quote(ticker)

    noise = list(Message.objects.filter(source="twitter"))[:33]
    noise += list(Message.objects.filter(source="stocktwits"))[:33]
    noise += list(Message.objects.filter(source="reddit"))[:33]
    random.shuffle(noise)

    focus = list(Message.objects.filter(focus=ticker.upper()))
    random.shuffle(focus)
    company = Company.objects.filter(ticker=ticker)
    return render(request, 'detail.html', {
        "company": company,
        "stock": stock_detail,
        "streamer": noise,
        "twitter_check": "/check/twitter/{}/".format(ticker),
        "stocktwit_check": "/check/stocktwit/{}/".format(ticker),
        "reddit_check": "/check/reddit/{}/".format(ticker),
    })


def load(request, ticker):
    return render(request, 'loading.html', {"redirect": "/detail/{}/".format(ticker), "load_link": "/check/{}/".format(ticker)})


def test(request, load_type, ticker):
    ticker = ticker.upper()
    messages = get_stock_comments(ticker)
    if load_type.lower() == "stocktwit":
        for index, message in enumerate(messages):
            message = format_into_table(message, ticker)
            messages[index] = message
            save_message(message)
        return JsonResponse(messages, safe=False)
    if load_type.lower() == "reddit":
        try:
            companies = get_companies()
            query = ticker_to_name(companies, ticker)
            reddit_messages = scrape_reddit(ticker, query)
            save_reddit_articles(reddit_messages)
        except KeyError:
            reddit_messages = []
        return JsonResponse(reddit_messages, safe=False)
    if load_type.lower() == "twitter":
        tweets = get_twitter_comments(ticker)
        for index, message in enumerate(tweets):
            message = json_into_table(message, ticker)
            tweets[index] = message

        return JsonResponse(tweets, safe=False)

    return HttpResponseNotFound()
