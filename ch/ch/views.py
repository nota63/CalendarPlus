from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import View

# homepage
def home(request):
    return render(request,'index.html')

# HOME.HTML HAS SOME FEATURES----

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



# Check email middleware

@login_required
def update_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, "Email updated successfully! 🎉")
            return redirect("landing_page")  
        messages.error(request, "Please enter a valid email.")
    
    return render(request, "middlewares/update_email.html")


# first time guide 
class GuideView(View):
    template_name = "middlewares/guide.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        
        request.session["seen_guide"] = True
        return redirect("organization_list") 