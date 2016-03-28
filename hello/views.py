from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'index.html')
    # return HttpResponse('Hello from Python!')


def detail(request):
    return render(request, 'detail.html')
