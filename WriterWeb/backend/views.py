from django.shortcuts import render, redirect

from django.core.serializers import serialize
from django.http import JsonResponse
from django.apps import apps
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

# Create your views here.

#load models
from django.contrib.auth.models import User
from .models import *
from django.apps import apps
Key = apps.get_model('frontend', 'Key')
Urls = apps.get_model('frontend', 'Urls')

#exception
from django.core.exceptions import ObjectDoesNotExist
from .throw_error import Err as Throwerror
#models.Q tạo truy vấn phức tạp
from django.db.models import Q as Query, Avg, Count
from django.db import models

import random

import pytz
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')

##################################################################################################################################################
#route backend/{key}/account/{account_id} v
#GET: lấy thông tin của Account
#POST: cập nhật thông tin
#DELETE: xóa tài khoản
import re
def makeUrl(url):
    if (bool(re.match(r'^/http.*$', url))):
        url=url.replace('/http', 'http')
    return url.replace('%3A', ':/')

Err = Throwerror()

#@csrf_exempt
def account(request, key, account_id):
    userKey = Key.objects.get(key=key)
    try:
        acc=Account.objects.get(id=account_id)
        if userKey.user != acc.user:
            return JsonResponse(Err.permissionDeny())
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Account'))
    loging_in = True
    if request.method == 'GET': #v
        author = AuthorProfile.objects.get(account=acc)
        reader = ReaderProfile.objects.get(account=acc)
        account_info = {
            'loging_in' : loging_in,
            'name' : acc.user.username,
            'profile_name' : acc.profile_name,
            'email' : acc.user.email,
            'first_name' : acc.user.first_name,
            'last_name' : acc.user.last_name,
            'company' : acc.company,
            'profile_img_url' : makeUrl(acc.profile_image.url),
            'author_exp' : author.exp,
            'reader_exp' : reader.exp
        }
        resdata=Err.none()
        resdata.update({'message':'Get account info','account_id':account_id, 'account' : account_info})
        return JsonResponse(resdata)
    if request.method == 'POST': #v
        if not loging_in:
            return JsonResponse(Err.permissionDeny())
        acc.user.first_name=request.POST.get('first_name', acc.user.first_name)
        acc.user.last_name=request.POST.get('last_name', acc.user.last_name)
        acc.user.email=request.POST.get('email', acc.user.email)
        acc.company=request.POST.get('company', acc.company)
        author = AuthorProfile.objects.get(account=acc)
        reader = ReaderProfile.objects.get(account=acc)
        author.exp = request.POST.get('author_exp', author.exp)
        reader.exp = request.POST.get('reader_exp', reader.exp)
        acc.save()
        author.save()
        reader.save()
        acc.user.save()
        new_account_info = {
            'name' : acc.user.username,
            'email' : acc.user.email,
            'first_name' : acc.user.first_name,
            'last_name' : acc.user.last_name,
            'company' : acc.company,
            'profile_img_url' : makeUrl(acc.profile_image.url),
            'author_exp' : author.exp,
            'reader_exp' : reader.exp
        }
        resdata=Err.none()
        resdata.update({'message':'Update account', 'account_id':account_id, 'account':new_account_info})
        return JsonResponse(resdata)
    if request.method == 'DELETE': #v
        if not loging_in:
            return JsonResponse(Err.permissionDeny())
        author = AuthorProfile.objects.get(account=acc)
        reader = ReaderProfile.objects.get(account=acc)
        account_info = {
            'name' : acc.user.username,
            'email' : acc.user.email,
            'first_name' : acc.user.first_name,
            'last_name' : acc.user.last_name,
            'company' : acc.company,
            'profile_img_url' : makeUrl(acc.profile_image.url),
            'author_exp' : author.exp,
            'reader_exp' : reader.exp
        }
        acc.user.delete()
        resdata=Err.none()
        resdata.update({'message':'Delete account', 'account_id':account_id, 'deleted_account': account_info})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/login : đăng nhập v
#POST: gửi tín hiệu đăng nhập
#DELETE: gửi tín hiệu đăng xuất
from django.contrib.auth import authenticate, login as djlogin, logout

def login(request, key):
    if request.user.is_authenticated and request.method == 'DELETE':
        userKey = Key.objects.get(key=key)
        if userKey.user != request.user:
            return redirect(reverse('oops'))
        logout(request)
    elif not request.user.is_authenticated and request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        userKey = Key.objects.get(key=key)
        user = authenticate(request, username=username, password=password)
        if userKey.user != user:
            return redirect(reverse('oops'))
        if user is not None:
            djlogin(request, user)
    return redirect(reverse('home'))

##################################################################################################################################################
#route backend/{key}/register : đăng ký v
#POST: gửi tín hiệu đăng ký
from faker import Faker
fake = Faker()
def register(request, key):
    if key != 888:
        return redirect(reverse('oops'))
    if request.user.is_authenticated:
        return redirect(reverse('oops'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repass = request.POST.get('repass')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', None)
        email = request.POST.get('email')
        company = request.POST.get('company', None)
        if not username:
            return redirect(reverse('oops'))
        if User.objects.filter(username=username).exists():
            return redirect(reverse('oops'))
        if not first_name:
            return redirect(reverse('oops'))
        if not email:
            return redirect(reverse('oops'))
        if len(password) < 6:
            return redirect(reverse('oops'))
        if password != repass:
            return redirect(reverse('oops'))
        pen_name=request.POST.get('pen_name', str(username).upper())
        profile_name = request.POST.get('profile_name', str(first_name+last_name).upper())
        user = User.objects.create_user(username=username, password=password)
        user.last_name='-' if not last_name else last_name
        user.first_name=first_name
        user.email=email
        user.save()
        imgurl=fake.image_url()
        while "placekitten.com" in imgurl:
            imgurl = fake.image_url()
        acc = Account.objects.create(user=user, company=company, profile_image = imgurl, profile_name=profile_name)
        AuthorProfile.objects.create(account=acc, pen_name=pen_name)
        ReaderProfile.objects.create(account=acc)
        return redirect(reverse('registerdone'))
    return redirect(reverse('oops'))

##################################################################################################################################################
#route backend/{key}/newuniverse: tạo vũ trụ mới v
def makeBool(string):
    if string == 'True':
        return True
    return False
def choisePublic(string):
    if string == 'public' or string == 'subcribe' or string == 'private':
        return string
    return 'public'
#@csrf_exempt
def newuniverse(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if not request.user.is_authenticated: #v
        return JsonResponse(Err.requiredLogin())
    if request.method == "POST": #v
        user = request.user
        acc = Account.objects.get(user=user)
        auth_pf = AuthorProfile.objects.get(account=acc)
        master = auth_pf
        title = request.POST.get('title')
        if not title:
            return JsonResponse(Err.requiredVariable('title'))
        cover_img = fake.image_url()
        world_map = fake.image_url()
        rules = request.POST.get('rules')
        if not rules:
            return JsonResponse(Err.requiredVariable('rules'))
        free_add_chapter = makeBool(request.POST.get('free_add_chapter', 'True'))
        public = choisePublic(request.POST.get('public', 'public'))
        uni = Universe.objects.create(master=master, title=title, cover_img=cover_img, world_map=world_map, rules=rules, free_add_chapter=free_add_chapter, public=public)
        uni_info = {
            'message' : 'Create new universe',
            'master' : uni.master.pen_name, #continue
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'free_add_chapter' : uni.free_add_chapter,
            'public' : uni.public,
            'genres' : {},
            'chapters' : {}
        }
        resdata=Err.none()
        resdata.update(uni_info)
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/universe/{uni_id} v
#GET: Lấy thông tin về vũ trụ
#POST: Thay đổi title và rule
#DELETE: Xóa vũ trụ
#@csrf_exempt
def universe(request, key, uni_id):
    try:
        uni=Universe.objects.get(id=uni_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Universe'))
    is_master = False
    if request.user.is_authenticated: 
        if request.user == uni.master.account.user:
            is_master = True
    if request.method == 'GET': #v
        gen_dict = {genre.id: genre.name for i, genre in enumerate(uni.genres.all())}
        chapters = Chapter.objects.filter(universe=uni)
        uni_chapter={}
        if chapters.exists():
            uni_chapter = {chapter.id: {chapter.title : chapter.author.pen_name} for i, chapter in enumerate(chapters)}
        uni_info = {
            'message' : 'Get universe info',
            'uni_id' : uni.id,
            'master' : {
                'id': uni.master.account.id, 
                'info' : {
                    'pen_name': uni.master.pen_name, 
                    'writing_exp':uni.master.exp,
                    'profile_img':makeUrl(uni.master.account.profile_image.url)
                    }
                },
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'free_add_chapter' : uni.free_add_chapter,
            'public' : uni.public,
            'genres' : gen_dict,
            'chapters' : uni_chapter
        }
        resdata=Err.none()
        resdata.update(uni_info)
        return JsonResponse(resdata)
    if request.method == 'POST':
        if (not is_master):
            return JsonResponse(Err.permissionDeny())
        uni.title = request.POST.get('title', uni.title)
        uni.rules = request.POST.get('rules', uni.rules)
        uni.save()
        gen_dict = {genre.id: genre.name for i, genre in enumerate(uni.genres.all())}
        uni_info={
            'message' : 'Change title and/or rules',
            'master' : uni.master.account.user.username,
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'genres' : gen_dict
        }
        resdata=Err.none()
        resdata.update(uni_info)
        return JsonResponse(resdata)
    if request.method == 'DELETE':
        if (not is_master):
            return JsonResponse(Err.permissionDeny())
        gen_dict = {genre.id: genre.name for i, genre in enumerate(uni.genres.all())}
        uni_info = {
            'message' : 'Delete universe success',
            'master' : uni.master.account.user.username,
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'genres' : gen_dict
        }
        uni.delete()
        resdata=Err.none()
        resdata.update(uni_info)
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/newgenre: tạo thể loại mới v
#@csrf_exempt
def newgenre(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', None)
        if not name:
            return JsonResponse(Err.requiredVariable('name'))
        if Genre.objects.filter(name=name).exists():
            return JsonResponse(Err.alreadyExists('genre'))
        genre = Genre.objects.create(name=name, description=description)
        resdata=Err.none()
        resdata.update({'messages': 'Add new genre success', 'genre':{'name':genre.name, 'description':genre.description}})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/universe/{uni_id}/genre/{genre_id} : thêm hoặc xóa tag thể loại cho vũ trụ v
#PUT: thêm
#DELETE: xóa
#@csrf_exempt
def universe_genre(request, key, uni_id, genre_id):
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    try:
        uni=Universe.objects.get(id=uni_id)
        genre=Genre.objects.get(id=genre_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Universe or genre'))
    is_master = False
    if request.user.is_authenticated:
        if request.user == uni.master.account.user:
            is_master = True
    if request.method == 'PUT':
        if (not is_master):
            return JsonResponse(Err.permissionDeny())
        if uni.genres.filter(id=genre_id).exists():
            return JsonResponse(Err.alreadyExists(genre))
        else:
            uni.genres.add(genre)
            resdata=Err.none()
            resdata.update({'message':'Already add '+genre.name+' to '+uni.title})
            return JsonResponse(resdata)
    if request.method == 'DELETE':
        if (not is_master):
            return JsonResponse(Err.permissionDeny())
        if not uni.genres.filter(id=genre_id).exists():
            return JsonResponse(Err.alreadyExists('genre has\'t'))
        else:
            uni.genres.remove(genre)
            resdata=Err.none()
            resdata.update({'message':'Already remove '+genre.name+' from '+uni.title})
            return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/universe/{uni_id}/localmaps: v
#GET: lấy thông tin local_map của vũ trụ
#@csrf_exempt
def localmaps(request, key, uni_id):
    try:
        universe = Universe.objects.get(id=uni_id)
        localMaps = LocalMap.objects.filter(universe=universe)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Universe or localmap'))
    if request.method == 'GET':
        localmaps_list = { localmap.local_name : makeUrl(localmap.local_img.url) for i, localmap in enumerate(localMaps)}
        resdata=Err.none()
        resdata.update({'message':'Get localmaps of universe', 'localmaps_list' : localmaps_list})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/universe/{uni_id}/newlocalmap: thêm localmap mới (đang phát triển)
#@csrf_exempt
def newlocalmap(request, key, uni_id):
    return JsonResponse({'message':'On developping'})

##################################################################################################################################################
#route backend/{key}/universe/{uni_id}/localmap/{map_id}: thay đổi localname v
#@csrf_exempt
def universe_localmap(request, key, uni_id, map_id):
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    try:
        universe = Universe.objects.get(id=uni_id)
        local = LocalMap.objects.get(id=map_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Universe or localmap'))
    is_master = False
    if request.user == universe.master.account.user:
        is_master == True
    if request.method=='POST':
        localname=request.POST.get('localname', local.local_name)
        local.local_name=localname
        local.save()
        resdata=Err.none()
        resdata.update({'message':'Changed local name'})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/universe/{uni_id}/newchapter v
#@csrf_exempt
def newchapter(request, key, uni_id):
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    try:
        uni = Universe.objects.get(id=uni_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Universe'))
    if request.method == 'POST':
        acc = Account.objects.get(user=request.user)
        auth = AuthorProfile.objects.get(account=acc)
        title = request.POST.get('title')
        if not title:
            return JsonResponse(Err.requiredVariable('title'))
        intro = request.POST.get('intro', 'No intro')
        chapter = Chapter.objects.create(universe=uni, author=auth, title=title, intro=intro)
        chapter_info={
            'message' : 'Get chapter info',
            'author' : chapter.author.pen_name,
            'universe' : chapter.universe.title,
            'title' : chapter.title,
            'intro' : chapter.intro,
            'accept' : chapter.accept,
            'paragraph_ids'  : {}
        }
        resdata=Err.none()
        resdata.update(chapter_info)
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/chapter/{chapter_id} v
#GET: lấy thông tin chapter
#POST: Cập nhật
#DELETE: xóa chapter
#@csrf_exempt
def check_key(json_data, key):
    have_next=False
    have_prev=False
    keys = list(json_data.keys())
    index = keys.index(key)
    have_prev = index > 0
    have_next = index < len(keys) - 1
    prev_id = keys[index - 1] if index > 0 else None
    next_id = keys[index + 1] if index < len(keys) - 1 else None
    return {
        'have_prev' : have_prev,
        'prev_id' : prev_id,
        'have_next' : have_next,
        'next_id' : next_id,
    }

def chapter(request, key, chapter_id):
    try:
        chapter=Chapter.objects.get(id=chapter_id)
        paragraphs = Paragraph.objects.filter(chapter = chapter).order_by('ordinal_number')
        chapters = Chapter.objects.filter(universe = chapter.universe)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Chapter'))
    is_master = False
    if request.user.is_authenticated:
        if request.user == chapter.universe.master.account.user:
            is_master = True
    is_auth = False
    if request.user.is_authenticated:
        if request.user == chapter.author.account.user:
            is_master = True
    if request.method == 'GET':
        paragraph_ids = {paragraph.ordinal_number: {'id' : paragraph.id} for i,paragraph in enumerate(paragraphs)}
        orther_chapters = {c.id: c.title for i, c in enumerate(chapters)}
        chapter_ratings = Rating.objects.filter(chapter=chapter)
        average_rating = chapter_ratings.aggregate(Avg('start'))['start__avg']
        chapter_comment_count = Comment.objects.filter(chapter=chapter).count()
        shared_count = SharedPost.objects.filter(chapter=chapter).count()
        chapter_info={
            'message' : 'Get chapter info',
            'id' : str(chapter_id),
            'author' : chapter.author.pen_name,
            'universe' : chapter.universe.title,
            'title' : chapter.title,
            'intro' : chapter.intro,
            'accept' : chapter.accept,
            'paragraph_ids'  : paragraph_ids,
            'orther_chapters' : orther_chapters,
            'image' : makeUrl(chapter.universe.cover_image.url),
            'a_image' : makeUrl(chapter.author.account.profile_image.url),
            'author_lv' : chapter.author.exp // 10,
            'average_rating' : average_rating,
            'chapter_comment_count' : chapter_comment_count,
            'shared_count' : shared_count
        }
        chapter_info.update(check_key(chapter_info['orther_chapters'], chapter_id))
        return JsonResponse(chapter_info)
    if request.method == "POST":
        if (not is_master and not is_auth):
            return JsonResponse(Err.permissionDeny())
        chapter.title = request.POST.get('title', chapter.title)
        chapter.intro = request.POST.get('intro', chapter.intro)
        accept = request.POST.get('accept')
        if accept is not None:
            if(not is_master):
                return JsonResponse(Err.permissionDeny())
            chapter.accept = accept
        chapter.save()
        paragraph_ids = {paragraph.ordinal_number: {'id' : paragraph.id} for i,paragraph in enumerate(paragraphs)}
        chapter_info={
            'message' : 'Update title',
            'author' : chapter.author.pen_name,
            'universe' : chapter.universe.title,
            'title' : chapter.title,
            'intro' : chapter.intro,
            'accept' : chapter.accept,
            'paragraph_ids'  : paragraph_ids
        }
        resdata=Err.none()
        resdata.update({chapter_info})
        return JsonResponse(resdata)
    if request.method == "DELETE":
        if (not is_master and not is_auth):
            return JsonResponse(Err.permissionDeny())
        paragraph_ids = {paragraph.ordinal_number: {'id' : paragraph.id} for i,paragraph in enumerate(paragraphs)}
        chapter_info={
            'message' : 'Delete chapter',
            'author' : chapter.author.pen_name,
            'universe' : chapter.universe.title,
            'title' : chapter.title,
            'intro' : chapter.intro,
            'accept' : chapter.accept,
            'paragraph_ids'  : paragraph_ids
        }
        chapter.delete()
        return JsonResponse(chapter_info)
    return ({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/{key}/parargaph/{paragraph_id} v
#GET: lấy thông tin paragraph
#POST: Cập nhật
#DELETE: xóa paragraph
#@csrf_exempt
def paragraph(request, key, paragraph_id):
    try:
        para = Paragraph.objects.get(id=paragraph_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Paragraph'))
    if request.method == 'GET':
        resdata=Err.none()
        resdata.update({'content' : para.content})
        return JsonResponse(resdata)
    if request.method == 'POST':
        new_content = request.POST.get(Err.none().update('new_content', para.content))
        para.content=new_content
        para.save()
        resdata=Err.none()
        resdata.update({'new_content': para.content})
        return JsonResponse(resdata)
    if request.method == 'DELETE':
        para.delete()
        resdata=Err.none()
        resdata.update({'message':'Delete paragraph success'})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/chapter/{chapter_id}/newparagraph: thêm paragraph mới v
#@csrf_exempt
def newparagraph(request, key, chapter_id):
    if request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Chapter'))
    auth_user = chapter.author.account.user
    if not auth_user == request.user:
        return JsonResponse(Err.permissionDeny())
    if request.method == 'POST':
        content=request.POST.get('content')
        if not content:
            return JsonResponse(Err.requiredVariable('content'))
        paragraph = Paragraph.objects.create(chapter=chapter, content=content)
        resdata=Err.none()
        resdata.update({'message':'Write paragraph success', 'content':paragraph.content})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/see/{account_id}/posts : lấy post theo user.favorite_genre và user->contact->otheruser->post v
# #@csrf_exempt
def posts(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    reader = ReaderProfile.objects.get(account=account)
    posts_by_tag = {}
    has_favorite_tag = True
    favorite_tags = FavoriteGenre.objects.filter(reader=reader)
    if favorite_tags.count() == 0:
        has_favorite_tag=False
    if has_favorite_tag:
        #object query dùng để lưu truy vấn kiểu: (genres==tag1) | (genres==tag2) ...
        query = Query()
        for tag in favorite_tags:
            query |= Query(genres=tag.genre)
        matching_universes = Universe.objects.filter(query).distinct() #distinct() dùng để loại các vũ trụ trùng lặp trong danh sách
        if matching_universes.count() != 0:
            matching_chapters = []
            for universe in matching_universes:
                chapters = Chapter.objects.filter(universe=universe)
                for chapter in chapters:
                    matching_chapters.append(chapter)
            if matching_chapters.__len__ != 0:
                for chapter in matching_chapters:
                    _posts = SharedPost.objects.filter(chapter=chapter).order_by('created_at')
                    if _posts.count() != 0:
                        for post in _posts:
                            keyobj = Key.objects.get(key=key)
                            if Urls.objects.filter(url = 'touser@'+str(post.reader.account.user.id), key=keyobj):
                                middlekey = Urls.objects.get(url = 'touser@'+str(post.reader.account.user.id), key=keyobj).middlekey
                            else:
                                while True:
                                    newmiddlekey = random.randint(100000, 999999)
                                    if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                                        break
                                Urls.objects.create(key=keyobj, middlekey=newmiddlekey, url='touser@'+str(post.reader.account.user.id), type='u')
                                middlekey = newmiddlekey
                            chapter_ratings = Rating.objects.filter(chapter=post.chapter)
                            average_rating = chapter_ratings.aggregate(Avg('start'))['start__avg']
                            chapter_comment_count = Comment.objects.filter(chapter=post.chapter).count()
                            shared_count = SharedPost.objects.filter(chapter=post.chapter).count()
                            updateJson = {
                                post.id : {
                                    'content' : post.content, 
                                    'chapter_title' : post.chapter.title,
                                    'chapter_id': post.chapter.id,
                                    'user_post' : post.reader.account.profile_name,
                                    'avartar' : makeUrl(post.reader.account.profile_image.url),
                                    'account_to_acount_middlekey' : middlekey,
                                    'universe_img' : makeUrl(post.chapter.universe.cover_image.url),
                                    'universe_title' : post.chapter.universe.title,
                                    'time_stamp' : post.created_at.astimezone(vn_timezone).strftime("%d/%m/%Y %H:%M"),
                                    'chapter_intro' : post.chapter.intro,
                                    'chapter_author': post.chapter.author.pen_name,
                                    'author_avartar': makeUrl(post.chapter.author.account.profile_image.url),
                                    'is_accepted' : True if post.chapter.accept == 'accepted' else False,
                                    'chapter_star' : round(average_rating, 2) if average_rating is not None else '-',
                                    'count_cmt' : chapter_comment_count,
                                    'count_shared' : shared_count
                                }
                            }
                            posts_by_tag.update(updateJson)
    posts_by_contact = {}
    has_contact = True
    contacts = Contact.objects.filter(Query(user_from=account) | Query(user_to = account), confirm='accepted')
    if contacts.count() == 0:
        has_contact = False
    if has_contact:
        query = Query()
        for contact in contacts:
            other = contact.user_to
            if contact.user_to == request.user:
                other = contact.user_from
            other_account = other
            other_reader = ReaderProfile.objects.get(account=other_account)
            _posts=SharedPost.objects.filter(reader=other_reader).order_by('created_at')
            if _posts.count() != 0:
                for post in _posts:
                    keyobj = Key.objects.get(key=key)
                    if Urls.objects.filter(url = 'touser@'+str(post.reader.account.user.id), key=keyobj):
                        middlekey = Urls.objects.get(url = 'touser@'+str(post.reader.account.user.id), key=keyobj).middlekey
                    else:
                        while True:
                            newmiddlekey = random.randint(100000, 999999)
                            if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                                break
                        Urls.objects.create(key=keyobj, middlekey=newmiddlekey, url='touser@'+str(post.reader.account.user.id), type='u')
                        middlekey = newmiddlekey
                    chapter_ratings = Rating.objects.filter(chapter=post.chapter)
                    average_rating = chapter_ratings.aggregate(Avg('start'))['start__avg']
                    chapter_comment_count = Comment.objects.filter(chapter=post.chapter).count()
                    shared_count = SharedPost.objects.filter(chapter=post.chapter).count()
                    updateJson = {
                        post.id : {
                            'content' : post.content, 
                            'chapter_title' : post.chapter.title,
                            'chapter_id': post.chapter.id,
                            'user_post' : post.reader.account.profile_name,
                            'avartar' : makeUrl(post.reader.account.profile_image.url),
                            'account_to_acount_middlekey' : middlekey,
                            'universe_img' : makeUrl(post.chapter.universe.cover_image.url),
                            'universe_title' : post.chapter.universe.title,
                            'time_stamp' : post.created_at.astimezone(vn_timezone).strftime("%d/%m/%Y %H:%M"),
                            'chapter_intro' : post.chapter.intro,
                            'chapter_author': post.chapter.author.pen_name,
                            'author_avartar': makeUrl(post.chapter.author.account.profile_image.url),
                            'is_accepted' : True if post.chapter.accept == 'accepted' else False,
                            'chapter_star' : round(average_rating, 2) if average_rating is not None else '-',
                            'count_cmt' : chapter_comment_count,
                            'count_shared' : shared_count
                        }
                    }
                    posts_by_tag.update(updateJson)
    if not (has_favorite_tag or has_contact):
        return JsonResponse(Err.ortherErr({'message':'Add a favorite tag to see some posts'}))
    jsonres = Err.none()
    jsonres.update({'post_by_ftag' : posts_by_tag, 'post_by_contact' : posts_by_contact})
    return JsonResponse (jsonres)

def myposts(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    reader = ReaderProfile.objects.get(account=account)
    if request.method == 'GET':
        posts = SharedPost.objects.filter(reader=reader)
        postsJson = {}
        if posts.count() != 0:
            for post in posts:
                keyobj = Key.objects.get(key=key)
                if Urls.objects.filter(url = 'touser@'+str(post.reader.account.user.id)).filter(key=keyobj):
                    middlekey = Urls.objects.get(url = 'touser@'+str(post.reader.account.user.id), key=keyobj).middlekey
                else:
                    while True:
                        newmiddlekey = random.randint(100000, 999999)
                        if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                            break
                    Urls.objects.create(key=keyobj, middlekey=newmiddlekey, url='touser@'+str(post.reader.account.user.id), type='u')
                    middlekey = newmiddlekey
                chapter_ratings = Rating.objects.filter(chapter=post.chapter)
                average_rating = chapter_ratings.aggregate(Avg('start'))['start__avg']
                chapter_comment_count = Comment.objects.filter(chapter=post.chapter).count()
                shared_count = SharedPost.objects.filter(chapter=post.chapter).count()
                updateJson = {
                    post.id : {
                        'content' : post.content, 
                        'chapter_title' : post.chapter.title,
                        'chapter_id': post.chapter.id,
                        'user_post' : post.reader.account.profile_name,
                        'avartar' : makeUrl(post.reader.account.profile_image.url),
                        'account_to_acount_middlekey' : middlekey,
                        'universe_img' : makeUrl(post.chapter.universe.cover_image.url),
                        'universe_title' : post.chapter.universe.title,
                        'time_stamp' : post.created_at.astimezone(vn_timezone).strftime("%d/%m/%Y %H:%M"),
                        'chapter_intro' : post.chapter.intro,
                        'chapter_author': post.chapter.author.pen_name,
                        'author_avartar': makeUrl(post.chapter.author.account.profile_image.url),
                        'is_accepted' : True if post.chapter.accept == 'accepted' else False,
                        'chapter_star' : round(average_rating, 2) if average_rating is not None else '-',
                        'count_cmt' : chapter_comment_count,
                        'count_shared' : shared_count
                    }
                }
                postsJson.update(updateJson)
        jsonres = Err.none()
        jsonres.update({'posts' : postsJson})
        return JsonResponse (jsonres)

##################################################################################################################################################
#route backend/{key}/post/{post_id} v
#GET: lấy thông tin của bài đăng
#POST: cập nhật bài đăng
#DELETE: xóa bài đăng
#@csrf_exempt
def sharedPost(request, key, post_id):
    try:
        post = SharedPost.objects.get(id=post_id)
    except ObjectDoesNotExist:
        return JsonResponse(Err.objectDoesNotExists('Post'))
    reader = post.reader
    if request.method == 'GET':
        jsonrep = {
            'message':'Get post info',
            'postId': post.id,
            'content': post.content,
            'chapter' : {'id' : post.chapter.id, 'intro' : post.chapter.intro} if post.chapter != "DELETED" else 'DELETTED',
            'reader' : {'id' : reader.id, 'name' : reader.account.user.username},
            'created' : post.created_at
        }
        resdata=Err.none()
        resdata.update(jsonrep)
        return JsonResponse(resdata)
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    logined_account = Account.objects.get(user=request.user)
    logined_reader = ReaderProfile.objects.get(account=logined_account)
    if logined_reader != reader:
        return JsonResponse(Err.permissionDeny())
    if request.method == 'POST':
        content = request.POST.get('content', post.content)
        post.content=content
        post.save()
        jsonrep = {
            'message':'Get post info',
            'postId': post.id,
            'content': post.content,
            'chapter' : {'id' : post.chapter.id, 'intro' : post.chapter.intro} if post.chapter != "DELETED" else 'DELETTED',
            'reader' : {'id' : reader.id, 'name' : reader.account.user.username},
            'created' : post.created_at
        }
        resdata=Err.none()
        resdata.update({'message':'Update post', 'post' : jsonrep})
        return JsonResponse(resdata)
    if request.method == 'DELETE':
        post.delete()
        resdata=Err.none()
        resdata.update({'message':'Delete post success'})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/newpost: tạo post mới v
#@csrf_exempt
def newPost(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    reader = ReaderProfile.objects.get(account=account)
    if request.method == 'POST':
        content = request.POST.get('content', None)
        chapter_id = request.POST.get('chapter_id')
        if chapter_id is not None:
            try:
                chapter=Chapter.objects.get(id=chapter_id)
            except ObjectDoesNotExist:
                return (Err.objectDoesNotExists('Chapter'))
            new_post = SharedPost.objects.create(chapter=chapter, reader= reader, content=content)
            resdata=Err.none()
            resdata.update({'message':'Shared success', 'post':{'id':new_post.id, 'chapter':new_post.chapter.title, 'content':new_post.content}})
            return JsonResponse(resdata)
        else:
            return JsonResponse(Err.requiredVariable('chapter_id'))
    return JsonResponse(Err.unsuportedMethod)

##################################################################################################################################################
#route backend/{key}/favoritetag/{account_id}: v
#GET:lấy các favorite tag
#PUT:chọn favorite tag mới
#POST:thay đổi thứ tự favorite tag
#DELETE:xóa tag
#@csrf_exempt
def favorite(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    reader = ReaderProfile.objects.get(account=account)
    if request.method == 'GET':
        tags = FavoriteGenre.objects.filter(reader=reader).order_by('pin_number')
        tags_json = {tag.genre.id : tag.genre.name for i,tag in enumerate(tags)}
        resdata=Err.none()
        resdata.update({'message':'Get all favorite tag', 'tags': tags_json})
        return JsonResponse(resdata)
    if request.method == 'PUT':
        genre_id = request.PUT.get('genre_id')
        if genre_id is None:
            return JsonResponse(Err.requiredVariable('genre_id'))
        try:
            genre = Genre.objects.get(id=genre_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Genre'))
        if FavoriteGenre.objects.filter(reader=reader, genre=genre).exists():
            return JsonResponse(Err.alreadyExists('favorite genre'))
        newFtags = FavoriteGenre.objects.create(reader=reader, genre=genre, pin_number=1)
        resdata=Err.none()
        resdata.update({'message':'Add new favorite tag', 'tag': newFtags.genre.name, 'genre_id':newFtags.genre.id})
        return JsonResponse(resdata)
    if request.method == 'POST':
        genre_id = request.POST.get('genre_id')
        if genre_id is None:
            return JsonResponse(Err.requiredVariable('genre_id'))
        try:
            genre = Genre.objects.get(id=genre_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Genre'))
        if not FavoriteGenre.objects.filter(reader=reader, genre=genre).exists():
            return JsonResponse(Err.ortherErr('You dont have this favorite genre'))
        pin_number = request.POST.get('pin_number', 1)
        favoriteGengre = FavoriteGenre.objects.get(reader=reader, genre=genre)
        favoriteGengre.pin_number=pin_number
        favoriteGengre.save()
        resdata=Err.none()
        resdata.update({'message':'Update pin number', 'gengre': favoriteGengre.genre.name, 'gengre_id':favoriteGengre.genre.id, 'new_pin_number':favoriteGengre.pin_number})
        return JsonResponse(resdata)
    if request.method == 'DELETE':
        genre_id = request.DELETE.get('genre_id')
        if genre_id is None:
            return JsonResponse(Err.requiredVariable('genre_id'))
        try:
            genre = Genre.objects.get(id=genre_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Genre'))
        if not FavoriteGenre.objects.filter(reader=reader, genre=genre).exists():
            return JsonResponse(Err.ortherErr('You dont have this favorite genre'))
        favoriteGengre = FavoriteGenre.objects.get(reader=reader, genre=genre)
        favoriteGengre.delete()
        resdata=Err.none()
        resdata.update({'message':'Deleted favorite tag', 'name':favoriteGengre.genre.name})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

##################################################################################################################################################
#route backend/{key}/pinuniverse/{account_id}: v
#GET:lấy các pinuniverse
#PUT:chọn pinuniverse mới
#POST:thay đổi thứ tự pinuniverse
#DELETE:xóa pinuniverse

#@csrf_exempt
def pinuniverses(request, key):
    userhasKey = Key.objects.get(key=key).user
    account=Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    reader = ReaderProfile.objects.get(account=account)
    if request.method == 'GET':
        pinuniverses_list=PinUniverse.objects.filter(reader=reader).order_by('pin_number')
        pinuniverses_json = {pinuniverse.universe.id : {
                'title': pinuniverse.universe.title,
                'chapter_count' : Chapter.objects.filter(universe=pinuniverse.universe).count(),
                'image' : makeUrl(pinuniverse.universe.cover_image.url),
                'rules' : pinuniverse.universe.rules,
                'firstchapter_id' : Chapter.objects.filter(universe=pinuniverse.universe).first().id
            } for i,pinuniverse in enumerate(pinuniverses_list)}
        resdata=Err.none()
        resdata.update({'message' : 'Get pinuniveses', 'pinuniverses':pinuniverses_json})
        return JsonResponse(resdata)
    if request.method == 'PUT':
        universe_id = request.PUT.get('universe_id', None)
        if universe_id is None:
            return JsonResponse(Err.requiredVariable('universe_id'))
        try:
            universe = Universe.objects.get(id=universe_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Universe'))
        if PinUniverse.objects.filter(reader=reader, universe=universe).exists():
            return JsonResponse({'message':'You already has this universe in pin'})
        new_pinuni=PinUniverse.objects.create(reader=reader, universe=universe)
        return JsonResponse({'message':'Add pin universe success', 'universe' : {new_pinuni.universe.id:new_pinuni.universe.title}})
    if request.method == 'POST':
        universe_id = request.POST.get('universe_id', None)
        universe_id = request.POST.get('universe_id', None)
        if universe_id is None:
            return JsonResponse({'message':'Required universe_id'})
        try:
            universe = Universe.objects.get(id=universe_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Universe'))
        if not PinUniverse.objects.filter(reader=reader, universe=universe).exists():
            return JsonResponse(Err.alreadyExists('pin universe hasnt'))
        pinuni = PinUniverse.objects.get(reader=reader, universe=universe)
        pin_number = request.POST.get('pin_number', pinuni.pin_number)
        pinuni.pin_number=pin_number
        pinuni.save()
        resdata=Err.none()
        resdata.update({'message':'Change pin_number success', 'universe' : {'id' : pinuni.universe.id, 'title' : pinuni.universe.title, 'new_pin_number': pinuni.pin_number}})
        return JsonResponse(resdata)
    if request.method == 'DELETE':
        universe_id = request.DELETE.get('universe_id', None)
        if universe_id is None:
            return JsonResponse(Err.requiredVariable('universe_id'))
        try:
            universe = Universe.objects.get(id=universe_id)
        except ObjectDoesNotExist:
            return JsonResponse(Err.objectDoesNotExists('Universe'))
        if not PinUniverse.objects.filter(reader=reader, universe=universe).exists():
            return JsonResponse(Err.alreadyExists('pin universe hasnt'))
        pinuni = PinUniverse.objects.get(reader=reader, universe=universe)
        pinuni.delete()
        resdata=Err.none()
        resdata.update({'message':'Deleted pin success'})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

#route backend/{key}/reading
def reading(request, key):
    userhasKey = Key.objects.get(key=key).user
    account=Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if not request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    reader = ReaderProfile.objects.get(account=account)
    if request.method == 'GET':
        jsonres={'none' : True}
        readlogjson = {}
        if ReadLog.objects.filter(reader=reader).exists():
            reading_list = ReadLog.objects.filter(reader=reader).order_by('-updated_at')
            change_reading_list = []
            for readlog in reading_list:
                found = False
                if len(change_reading_list) !=0:
                    for c_readlog in change_reading_list:
                        if c_readlog.chapter.universe == readlog.chapter.universe:
                           found = True
                if not found:
                    change_reading_list.append(readlog)
            jsonres={'none' : False}
            for readlog in change_reading_list:
                readlogjson.update({
                    readlog.id: {
                        'universe' : readlog.chapter.universe.title,
                        'chapter' : readlog.chapter.title,
                        'chapter_id' : readlog.chapter.id,
                        'chapter_read_count': 
                            str(ReadLog.objects.filter(chapter=readlog.chapter, reader=readlog.reader).count()) 
                            + '/' 
                            + str(Chapter.objects.filter(universe=readlog.chapter.universe).count())
                    }}
                )
        jsonres.update({'logs': readlogjson})
        resdata=Err.none()
        resdata.update(jsonres)
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())
##################################################################################################################################################
#route backend/{key}/see/contacts: hiển thị contact và số lượng tin nhắn chưa xem v
#@csrf_exempt
def seecontacts(request, key):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse(Err.requiredLogin())
        account=Account.objects.get(user=request.user)
        query = Query(user_from=account, confirm='accepted') | Query(user_to=account, confirm='accepted')
        all_user_contacts=Contact.objects.filter(query)
        save_ids = []
        all_contacts_json = {}
        for contact in all_user_contacts:
            unseencount=0
            #người gửi là người còn lại, với: sender: true | false tương ứng với Contact.user_from | Contact.user_to đã gửi
            if account == contact.user_from:
                unseencount = Message.objects.filter(sender=False, is_read=False, contact=contact).count()
                save_ids.append(contact.user_to.id)
            elif account == contact.user_to:
                unseencount = Message.objects.filter(sender=True, is_read=False, contact=contact).count()
                save_ids.append(contact.user_from.id)
            add_json = {
                contact.id : {
                    'name' : contact.user_from.profile_name, 
                    'profile_img' : makeUrl(contact.user_from.profile_image.url), 
                    'unseencount' : unseencount
                } if account==contact.user_to else {
                    'name' : contact.user_to.profile_name, 
                    'profile_img' : makeUrl(contact.user_to.profile_image.url), 
                    'unseencount' :unseencount
                }
            }
            all_contacts_json.update(add_json)
        query = Query(user_from=account, confirm='waiting')
        sent_contacts = Contact.objects.filter(query)
        sent_contacts_json = {}
        for contact in sent_contacts:
            save_ids.append(contact.user_to.id)
            add_json= {
                contact.id : {
                    'name' : contact.user_to.profile_name,
                    'profile_img' : makeUrl(contact.user_to.profile_image.url),
                    'unseencount' : Message.objects.filter(sender=False, is_read=False, contact=contact).count()
                }
            }
            sent_contacts_json.update(add_json)
        query = Query(user_to=account, confirm='waiting')
        received_contacts = Contact.objects.filter(query)
        received_contacts_json = {}
        for contact in received_contacts:
            save_ids.append(contact.user_from.id)
            add_json= {
                contact.id : {
                    'name' : contact.user_from.profile_name,
                    'profile_img' : makeUrl(contact.user_from.profile_image.url),
                    'unseencount' : Message.objects.filter(sender=True, is_read=False, contact=contact).count()
                }
            }
            received_contacts_json.update(add_json)
        reader = ReaderProfile.objects.get(account=account)
        same_tag_users = get_similar_readers(reader).exclude(account_id__in=save_ids)
        same_tag_users_json = {}
        for reader in same_tag_users:
            add_json={
                reader.id : {
                    'name' : reader.account.profile_name,
                    'profile_img' : makeUrl(reader.account.profile_image.url),
                }
            }
            same_tag_users_json.update(add_json)
        resdata=Err.none()
        resdata.update({'message':'Get your contacts', 'contacts' : all_contacts_json, 'request_sent' : sent_contacts_json, 'request_received' : received_contacts_json, 'same_tag' : same_tag_users_json})
        return JsonResponse(resdata)
    return JsonResponse(Err.unsuportedMethod())

def get_similar_readers(reader):
    # Lấy thể loại yêu thích của người đọc đã nhập vào
    reader_genres = FavoriteGenre.objects.filter(reader=reader).values_list('genre', flat=True)
    
    # Lấy danh sách các người đọc có thể loại yêu thích giống nhau (trừ người đọc đã nhập vào)
    similar_readers = FavoriteGenre.objects.filter(
        genre__in=reader_genres
    ).exclude(
        reader=reader
    ).values_list('reader', flat=True).distinct()
    return ReaderProfile.objects.filter(id__in=similar_readers)

##################################################################################################################################################
#route backend/{key}/message/<contact_id>:
#GET: hiển thị đoạn tin nhắn
#PUT: soạn tin nhắn
#DELETE: thu hồi tin nhắn
#@csrf_exempt
def messages(request, key, contact_id):
    if request.user.is_authenticated:
        return JsonResponse(Err.requiredLogin())
    account=Account.objects.get(user=request.user)
    contact = Contact.objects.get(id=contact_id)
    if contact.user_from!=account and contact.user_to!=account:
        return JsonResponse(Err.objectDoesNotExists('your_contact'))
    if request.method == 'GET':
        messages_json={}
        _messages = Message.objects.filter(contact=contact).order_by('timestamp')
        for message in _messages:
            messages_json.update({
                message.timestamp.strftime("%d/%m/%Y-%H:%M:%S.%f") : {
                    'id': message.id,
                    'content': message.content,
                    'is_read': message.is_read,
                    'is_sender': True if (contact.user_from==account and message.sender==True) or (contact.user_to==account and message.sender==False) else False
                }
            })
        resdata=Err.none()
        resdata.update(messages_json)
        return JsonResponse(resdata)
    if request.method == "PUT":
        content = request.PUT.get('content', None)
        if (content == None):
            return JsonResponse(Err.requiredVariable('content'))
        newMessage = Message.objects.create(content=content, sender= True if contact.user_from==account else False)
    

##################################################################################################################################################
#route backend/{key}/comments/{chapter_id}

def comments(request, key, chapter_id):
    userhasKey = Key.objects.get(key=key).user
    account = Account.objects.get(user=request.user)
    if account.user != userhasKey:
        return JsonResponse(Err.permissionDeny())
    chapter = Chapter.objects.get(id = chapter_id)
    comments = Comment.objects.filter(chapter = chapter)
    comments_json = {}
    for comment in comments:
        keyobj = Key.objects.get(key=key)
        if Urls.objects.filter(url = 'touser@'+str(comment.reader.account.user.id), key=keyobj):
            middlekey = Urls.objects.get(url = 'touser@'+str(comment.reader.account.user.id), key=keyobj).middlekey
        else:
            while True:
                newmiddlekey = random.randint(100000, 999999)
                if not Urls.objects.filter(middlekey=newmiddlekey).exists():
                    break
                Urls.objects.create(key=keyobj, middlekey=newmiddlekey, url='touser@'+str(comment.reader.account.user.id), type='u')
                middlekey = newmiddlekey
        comments_json.update({
            comment.id : {
                'reader' : comment.reader.account.profile_name,
                'reader_account_middleware': middlekey,
                'reader_img' : makeUrl(comment.reader.account.profile_image.url),
                'comment' : comment.content,
                'created_at' : comment.created_at.astimezone(vn_timezone).strftime("%d/%m/%Y %H:%M")
            }
        })
    jsonres = Err.none()
    jsonres.update({'comments' : comments_json})
    return JsonResponse(jsonres)
##################################################################################################################################################

##################################################################################################################################################