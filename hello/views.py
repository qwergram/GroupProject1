# coding=utf-8
from __future__ import unicode_literals
from builtins import open
import random
import json
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from .models import Message, Company
from .stock_info import get_current_quote, top_movers
from .stocktwits import get_stock_comments, format_into_table, save_message
from .twitter_api import get_twitter_comments, json_into_table
from .logo_grab import main as logo_grab_main
from .reddit import (
    get_companies,
    ticker_to_name,
    save_reddit_articles,
    scrape_reddit
)


with open("hello/raw_data/company_to_ticker.json", 'r', encoding='utf-8') as f:
    stock_ticker_lookup = json.load(f)


def logo_api(request, ticker):
    url = logo_grab_main(ticker)
    return JsonResponse({"logo": url})


def ajax_load(request):
    return render(request, 'loading.html')


def index(request):
    """
    Requests the biggest movers then looks up the current data
    for those movers for a given index.
    """
    # Get biggest movers
    stock_mover = top_movers()

    # Get latest data
    stock_mover_quotes = {}
    for stock in stock_mover:
        all_of_quote = get_current_quote(stock.ticker)
        # Get jUut the fields you need from the result
        stock_mover_quotes[stock.ticker] = {
            k: all_of_quote.get(k, None) for k in ('Symbol', 'Name', 'Bid', 'Change', 'PercentChange')}

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
    if ticker.lower() in stock_ticker_lookup:
        ticker = stock_ticker_lookup[ticker.lower()]

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
