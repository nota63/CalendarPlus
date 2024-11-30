from django.shortcuts import render, redirect
from django.conf import settings


# homepage
def home(request):
    return render(request,'home.html')


