from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect




class AdminOnlyMiddleware:

    def __init__(self, get_response):
        self.get_response= get_response

    def __call__(self, request):

        restricted_urls=['/meet/count/','/meet/intro/']

        if request.path in restricted_urls:
            if not request.user.is_authenticated or not request.user.is_staff:
                 return HttpResponseForbidden("You do not have permission to access this urls, for any query contact your admin!")
        response= self.get_response(request)
        return response 
          