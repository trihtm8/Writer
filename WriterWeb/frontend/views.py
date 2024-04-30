from django.shortcuts import render, redirect
from django.template.loader import render_to_string
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
from datetime import timedelta

import requests
from django.apps import apps
Account = apps.get_model('backend', 'Account')

#route: home : trang chủ
def home(request):
    if request.user.is_authenticated:
        if Key.objects.filter(user=request.user).exists():
            if timezone.now()-Key.objects.get(user=request.user).touch > timedelta(hours=2):
                key = Key.objects.get(user=request.user)
                key.delete()
                return redirect(reverse('oops')+'?session_outtime=1')
        return render(request, 'html/index.html')
    loginForm = LoginForm()
    registerForm = RegisterForm()
    return render(request, 'html/login_register.html', {"loginForm":loginForm, "registerForm": registerForm})

#subroute router/{routename}
import re
def extract_number_chapter(string):
    match = re.match(r"readview@(\d+)$", string)
    if match:
        return int(match.group(1))
    else:
        return None

def router(request, routename):
    if not request.user.is_authenticated:
        return redirect(reverse('oops'))
    if routename == 'home':
        urlheader = createKey(request.user, 'header', 'f')
        urlleft = createKey(request.user, 'indexleft', 'f')
        urlmain = createKey(request.user, 'indexmain', 'f')
        urlright = createKey(request.user, 'indexright', 'f')
        urlheader.save()
        urlleft.save()
        urlmain.save()
        urlright.save()
        resdata=Err.none()
        resdata.update({'urlheader' : 'middleware/'+str(urlheader.middlekey)})
        resdata.update({'urlleft' : 'middleware/'+str(urlleft.middlekey)})
        resdata.update({'urlmain' : 'middleware/'+str(urlmain.middlekey)})
        resdata.update({'urlright' : 'middleware/'+str(urlright.middlekey)})
        return JsonResponse(resdata)
    if routename == 'personal':
        urlmain = createKey(request.user, 'personalmain', 'f')
        urlmain.save()
        resdata=Err.none()
        resdata.update({'urlmain' : 'middleware/'+str(urlmain.middlekey)})
        return JsonResponse(resdata)
    if routename == 'personalinfo':
        key = Key.objects.get(user = request.user)
        return personalinfo(request=request, key=key.key)
    if extract_number_chapter(routename) != None:
        return readview(request, extract_number_chapter(routename))
    if routename == 'friends':
        key = Key.objects.get(user = request.user)
        return friends(request, key.key)
    if routename == 'universes':
        key = Key.objects.get(user = request.user)
        return universes(request, key.key)
    return JsonResponse(Err.ortherErr('No route found'))

#route registerdone
def registerdone(request):
    loginForm = LoginForm()
    registerForm = RegisterForm()
    return render(request, 'html/login_register.html', {'alert':'Your account has been created, try login!', "loginForm":loginForm, "registerForm": registerForm})

#############################################################################################################################################
#routes with key

####
#index page
#route index/header/{key}
def indexheaderroute(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account  = Account.objects.get(user = request.user)
    id = account.id
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    response = requests.get('http://127.0.0.1:8000'+reverse('account_info', kwargs={'key' : key, 'account_id':id}), headers=headers, cookies=cookies)
    if (response.json()['err']):
        return redirect(reverse('oops'))
    avartar = response.json()['account']['profile_img_url']
    return render(request, 'html/subtemplate_router.html', {'route' : 'index/header', 'avartar' : avartar, 'logoutFormhtml': render_to_string('forms/subforms/logoutForm.html',request=request)})

#route index/left/{key}
def indexleftroute(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account  = Account.objects.get(user = request.user)
    id = account.id
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    response = requests.get('http://127.0.0.1:8000'+reverse('account_info', kwargs={'key' : key, 'account_id' : id}), headers=headers, cookies=cookies)
    if (response.json()['err']):
        return redirect(reverse('oops'))
    jres = response.json()
    avartar = jres['account']['profile_img_url']
    name = jres['account']['profile_name']
    gengreRes = requests.get('http://127.0.0.1:8000'+reverse('favoritetag', kwargs={'key' : key}), headers=headers, cookies=cookies)
    tags_data = gengreRes.json().get('tags', {})
    return render(request, 'html/subtemplate_router.html', {'route': 'index/left', 'avartar' : avartar, 'profilename' : name, 'tags': tags_data})

#route index/main/{key}
def indexmainroute(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account  = Account.objects.get(user = request.user)
    id = account.id
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    response = requests.get('http://127.0.0.1:8000'+reverse('see_posts', kwargs={'key' : key}), headers=headers, cookies=cookies)
    posts = response.json()['post_by_ftag']
    posts.update(response.json()['post_by_contact'])
    return render(request, 'html/subtemplate_router.html', {'route': 'index/main', 'posts' : posts})

#route index/right/key
def indexrightroute(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account  = Account.objects.get(user = request.user)
    id = account.id
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    pinuni_response = requests.get('http://127.0.0.1:8000'+reverse('pinuniverse', kwargs={'key' : key}), headers=headers, cookies=cookies)
    pinuniverses = pinuni_response.json()['pinuniverses']
    reading_response = requests.get('http://127.0.0.1:8000'+reverse('reading', kwargs={'key' : key}), headers=headers, cookies=cookies)
    logs=reading_response.json()['logs']
    contacts_response = requests.get('http://127.0.0.1:8000'+reverse('see_contacts', kwargs={'key' : key}), headers=headers, cookies=cookies)
    contacts = contacts_response.json()['contacts']
    return render(request, 'html/subtemplate_router.html', {'route': 'index/right', 'pinuniverses': pinuniverses, 'logs' : logs, 'contacts' : contacts})

####
#personal page
#route personal/main/{key}
def personalmain(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account= Account.objects.get(user = request.user)
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    myposts = requests.get('http://127.0.0.1:8000'+reverse('myposts', kwargs={'key' : key}), headers=headers, cookies=cookies)
    account_response = requests.get('http://127.0.0.1:8000'+reverse('account_info', kwargs={'key' : key, 'account_id' : account.id}), headers=headers, cookies=cookies)
    account = account_response.json()['account']
    account.update({'reader_lv' : account['reader_exp'] // 10, 'author_lv' : account['author_exp']//10})
    feed_html = render_to_string('subtemplates/personal/feed.html', {'posts' : myposts.json()['posts']})
    return render(request, 'html/subtemplate_router.html', {'route' : 'personal/intro', 'account' : account, 'main_content' : feed_html})

def personalinfo(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    account= Account.objects.get(user = request.user)
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    account_response = requests.get('http://127.0.0.1:8000'+reverse('account_info', kwargs={'key' : key, 'account_id' : account.id}), headers=headers, cookies=cookies)
    account = account_response.json()['account']
    return render(request, 'html/subtemplate_router.html', {'route' : 'personal/info', 'account' : account})

####
#readview

def readview(request, chapterid):
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    key = Key.objects.get(user = request.user).key
    chapter_response = requests.get('http://127.0.0.1:8000'+reverse('chapter_info', kwargs={'key' : key, 'chapter_id' : chapterid}), headers=headers, cookies=cookies)
    chapter_info = chapter_response.json()
    for keyi, value in chapter_info['paragraph_ids'].items():
        paragraph_content = requests.get('http://127.0.0.1:8000'+reverse('paragraph_info', kwargs={'key' : key, 'paragraph_id' : value['id']}), headers=headers, cookies=cookies)
        chapter_info['paragraph_ids'][keyi].update({'content' : paragraph_content.json()['content']})
    mainhtml = render_to_string('html/subtemplate_router.html', {
        'route' : 'readview/main', 
        'view_main' : render_to_string('subtemplates/readview/viewmain.html', { 'chapter_info' : chapter_info}),
        'chapter_info' : chapter_info
    })
    comments = requests.get('http://127.0.0.1:8000'+reverse('comments', kwargs={'key' : key, 'chapter_id' : chapterid}), headers=headers, cookies=cookies)
    comments = comments.json()['comments']
    righthtml = render_to_string('subtemplates/readview/comments.html', {'chapter_info' : chapter_info, 'comments' : comments})
    jsonres = Err.none()
    jsonres.update({'mainhtml' : mainhtml, 'righthtml' : righthtml})
    return JsonResponse(jsonres)

####
#freinds

def friends(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    contacts_response = requests.get('http://127.0.0.1:8000'+reverse('see_contacts', kwargs={'key' : key}), headers=headers, cookies=cookies)
    contacts = contacts_response.json()
    return render(request, 'html/subtemplate_router.html', {'route' : 'friends', 'contacts' : contacts})

####
#universes

def universes(request, key):
    userHasKey = Key.objects.get(key=key).user
    if userHasKey != request.user:
        return redirect(reverse('oops'))
    headers={key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    cookies = request.COOKIES
    pinuniverses = requests.get('http://127.0.0.1:8000'+reverse('pinuniverse', kwargs={'key' : key}), headers=headers, cookies=cookies)
    print(pinuniverses.json())
    return render(request, 'html/subtemplate_router.html', {'route' : 'universes', 'pinuniverses' : pinuniverses.json()['pinuniverses']})
    
###################################################################################################################################
#checking routes
#on "check/"

#route login
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

#route logout
def checkRegister(request):
    if request.user.is_authenticated:
        return JsonResponse(Err.requiredLogout())
    if request.method == 'POST':
        username = request.POST.get('username', None)
        if username == None:
            return JsonResponse(Err.requiredVariable('username'))
        if User.objects.filter(username=username):
            return JsonResponse(Err.requiredVariable('no_exists username'))
        password = request.POST.get('password', None)
        repass = request.POST.get('repass')
        if password is None:
            return JsonResponse(Err.requiredVariable('password'))
        if len(password) < 6:
            return JsonResponse(Err.requiredVariable('longer password'))
        if repass != password:
            return JsonResponse(Err.requiredVariable('matching re_password'))
        moreInfoRegisterForm1 = MoreInfoRegisterForm1()
        moreInfoRegisterForm2 = MoreInfoRegisterForm2()
        html_forms = render(request, 'html/moreinforegister.html', {
            'moreInfoRegisterForm1' : moreInfoRegisterForm1,
            'moreInfoRegisterForm2' : moreInfoRegisterForm2
        })
        return html_forms
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
        return redirect(reverse(urls.url, kwargs={'key': urls.key.key}))

#route oops : return oops site
def oops(request):
    session_outtime = False
    if 'session_outtime' in request.GET:
        session_outtime = True
        logout(request)
    return render(request, 'html/oops.html', {'session_outtime': session_outtime})

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
            url = Urls.objects.create(key=key, middlekey=newmiddlekey, url=urlroute, type=type)
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
    urls = Urls.objects.filter(key=key)
    if urls.exists():
        for url in urls:
            while True:
                newmiddlekey = random.randint(100000, 999999)
                if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                    break
            url.middlekey=newmiddlekey
            url.save()