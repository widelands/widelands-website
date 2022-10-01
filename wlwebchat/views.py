# Create your views here.
from django.shortcuts import render


def webchat(request):
    return render(request, "wlwebchat/index.html")
