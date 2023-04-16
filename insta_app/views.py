from urllib import request
from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from .models import Profiles,Instagram
from .tasks import check,add_user
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from celery.task import PeriodicTask
from datetime import timedelta


def index(request):
    profiles = Profiles.objects.all()
    instas = Instagram.objects.all()
    if request.method == "POST":
        if 'save' in request.POST:
            # Change the following variables to match your login information and the target profile's username.
                username = request.POST['username']
                password = request.POST['password']
                add_user.delay(username=username,password=password)
                messages.info(request,"Your request sent to server. If the profile is not added within 1 minute, try again. ")
                return render(request,'index.html',{'profiles':profiles,'instas':instas}) 
        else:
            messages.info(request, 'Error!!! Try again later...') 
    return render(request,'index.html',{'profiles':profiles,'instas':instas})



def login(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            login.username = request.POST['username']
            login.password = request.POST['password']

            user = auth.authenticate(username=login.username,password=login.password)
            if user is not None:
                auth.login(request, user)
                time.sleep(5)
                return redirect('index')
            else:
                messages.info(request, 'Username or Password is incorrect')    
                return redirect('login')
        if 'register' in request.POST:
            email = request.POST['email']
            password2 = request.POST['password2']
            reg_password = request.POST['regpassword']
            reg_username = request.POST['regusername']
            if reg_password == password2:
                if User.objects.filter(username=reg_username).exists():
                    messages.info(request, 'Registration is failed. Usarname already in use')
                    return redirect('login')
                elif User.objects.filter(email=email).exists():
                    messages.info(request, 'Registration is failed. Email already in use')
                    return redirect('login')
            else:
                messages.info(request, 'Registration is failed. Passwords must be same') 
                return redirect('login')
            user = User.objects.create_user(username=reg_username,email=email,password=reg_password)    
            user.save()        
            return redirect('login')
    return render(request, 'login.html')


def destroy(request, id):  
    profile = Instagram.objects.get(id=id)
    profile.delete()  
    return redirect("/") 


def logout(request):
    auth.logout(request)
    return redirect('login')