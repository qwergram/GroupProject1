from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .stocktwits import get_stock_comments, format_into_table, save_message


def index(request):
    return render(request, 'index.html')


def test(request, ticker):
    messages = get_stock_comments(ticker)
    for index, message in enumerate(messages):
        message = format_into_table(message, ticker)
        messages[index] = message
        save_message(message)

    return JsonResponse(messages, safe=False)


def detail(request):
    return render(request, 'detail.html')
