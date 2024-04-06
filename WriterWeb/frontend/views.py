from django.shortcuts import render, redirect
from .forms import *
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
import requests
import json
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as djlogin, logout
from .throw_error import Err as E
Err = E()

from .models import *

import random
from django.utils import timezone

#route: home/ : trang chủ
def home(request):
    if request.user.is_authenticated:
        return render(request, 'html/index.html')
    loginForm = LoginForm()
    registerForm = RegisterForm()
    return render(request, 'html/login_register.html', {"loginForm":loginForm, "registerForm": registerForm})


###################################################################################################################################
#checking routes
#on "check/"

#route login/
def checkLogin(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            return JsonResponse(Err.requiredLogout())
        if request.method == 'DELETE':
            url = createKey(request.user, 'login', 'b')
            resdata=Err.none()
            resdata.update({'message':'Check logout success', 'url':'backend/'+str(url.key.key)+'/login', 'method': 'DELETE'})
            return JsonResponse(resdata)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not username:
                return JsonResponse(Err.requiredVariable('username'))
            if not User.objects.filter(username=username).exists():
                return JsonResponse(Err.objectDoesNotExists('User'))
            if not password:
                return JsonResponse(Err.requiredVariable('password'))
            user = authenticate(request, username=username, password=password)
            if user is not None:
                url = createKey(user, 'login', type='b')
                resdata=Err.none()
                resdata.update({'message':'Check login success', 'loginUrl': 'backend/'+str(url.key.key)+'/login', 'method':'POST'})
                return JsonResponse(resdata)
            else:
                return JsonResponse(Err.requiredVariable('valid username or password'))
    return JsonResponse(Err.unsuportedMethod())

#################################################################################################################################
#middleware views, help redirect to some views

#route middleware/{middlekey}

from django.http import HttpResponseForbidden

def middleware(request, middlekey):
    urls = Urls.objects.get(middlekey=middlekey)
    if not request.user.is_authenticated:
        if not urls.url == 'login':
            return redirect(reverse('oops'))
        else:
            return redirect(reverse(urls.url, kwargs={'key': urls.key.key}))
    if not request.user == urls.key.user:
        return redirect(reverse('oops'))
    if urls.type == 'b':
        return redirect(reverse(urls.url, kwargs={'key': urls.key.key}))
    elif urls.type == 'f':
        return redirect(reverse(urls.url))

#route oops/ : return oops site
def oops(request):
    return render(request, 'html/oops.html')

#function create new Key
def createKey(user, urlroute, type):
    if Key.objects.filter(user=user).exists():
        key = Key.objects.get(user=user)
        touch(key)
        if Urls.objects.filter(key=key, url=urlroute).exists():
            url=Urls.objects.get(key=key, url=urlroute)
        else:
            while True:
                newmiddlekey = random.randint(100000, 999999)
                if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                    break
            url = Urls.objects.create(key=key, middlekey=newmiddlekey, url=urlroute)
    else:
        while True:
            newkey = random.randint(10000, 99999)
            if not Key.objects.filter(key=newkey):
                break
        while True:
            newmiddlekey = random.randint(100000, 999999)
            if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                break
        key = Key.objects.create(key=newkey, user=user, touch=timezone.now())
        url = Urls.objects.create(key=key, middlekey=newmiddlekey, url=urlroute, type=type)
    return url

def touch(key: Key):
    while True:
            newkey = random.randint(10000, 99999)
            if not Key.objects.filter(key=newkey):
                break
    key.key=newkey
    key.save()