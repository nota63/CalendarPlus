from django.shortcuts import render, redirect
from django.conf import settings


# homepage
def home(request):
    return render(request,'home.html')


# test the base ui

def test_base(request):
    return render(request,'base.html')


#  UI components

def styles(request):
    return render(request, 'index.html')

def weather(request):
    return render(request, 'weather.html')


def text_glow(request):
    return render(request,'ui/text_glow.html')

def slider(request):
    return render(request,'ui/slider.html')

def swipe_slider(request):
    return render(request,'ui/swipe_slider.html')

def stylish_cards(request):
    return render(request,'ui/stylish_cards.html')


def image_slider_2(request):
    return render(request, 'ui/image_slider2.html')