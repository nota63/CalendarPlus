from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Create your views here.


# register

def register(request):
    if request.method == 'POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form= UserCreationForm()    
    return render(request,'accounts/register.html',{'form':form})


# login
def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('landing_page')
    else:
        form=AuthenticationForm()    
    return render(request,'accounts/login.html',{'form':form})


# logout
def logout_view(request):
    logout(request)
    return redirect('login')

