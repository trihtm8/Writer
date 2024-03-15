from django.shortcuts import render

from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponse
from django.apps import apps
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

#load models
from django.contrib.auth.models import User
from .models import Account, AuthorProfile, ReaderProfile, Universe, Genre, Chapter, Paragraph, LocalMap, FavoriteGenre, Contact, SharedPost
#exception
from django.core.exceptions import ObjectDoesNotExist
#models.Q tạo truy vấn phức tạp
from django.db.models import Q as Query

##################################################################################################################################################
#route backend/account/{account_id} v
#GET: lấy thông tin của Account
#POST: cập nhật thông tin
#DELETE: xóa tài khoản
import re
def makeUrl(url):
    if (bool(re.match(r'^/http.*$', url))):
        url=url.replace('/http', 'http')
    return url.replace('%3A', ':/')

@csrf_exempt
def account(request, account_id):
    try:
        acc=Account.objects.get(id=account_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Account does not exists'})
    loging_in=False
    if request.user.is_authenticated:
        if request.user == acc.user:
            loging_in = True
    if request.method == 'GET':
        author = AuthorProfile.objects.get(account=acc)
        reader = ReaderProfile.objects.get(account=acc)
        account_info = {
            'loging_in' : loging_in,
            'name' : acc.user.username,
            'email' : acc.user.email,
            'first_name' : acc.user.first_name,
            'last_name' : acc.user.last_name,
            'company' : acc.company,
            'profile_img_url' : makeUrl(acc.profile_image.url),
            'author_exp' : author.exp,
            'reader_exp' : reader.exp
        }
        return JsonResponse({'message':'Get account info', 'account_id':account_id, 'account' : account_info})
    if request.method == 'POST':
        if not loging_in:
            return JsonResponse({'message':'You must login as owner user to change account info'})
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
        return JsonResponse({'message':'Update account', 'account_id':account_id, 'account':new_account_info})
    if request.method == 'DELETE':
        if not loging_in:
            return JsonResponse({'message':'You must login as owner user to delete account'})
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
        return JsonResponse({'message':'Delete account', 'account_id':account_id, 'deleted_account': account_info})
    return JsonResponse({'message':'Unsupported method!'})

##################################################################################################################################################
#route backend/login : đăng nhập v
#POST: gửi tín hiệu đăng nhập
#DELETE: gửi tín hiệu đăng xuất
from django.contrib.auth import authenticate, login as djlogin, logout
@csrf_exempt
def login(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            return JsonResponse({'message':'You alredy login, logout to login other account'})
        if request.method == 'DELETE':
            logout(request)
            return JsonResponse({'message':'Logout success'})
    else: 
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not username:
                return JsonResponse({'message':'Required username'})
            if not User.objects.filter(username=username).exists():
                return JsonResponse({'message':'Username does not exists'})
            if not password:
                return JsonResponse({'message':'Required password'})
            user = authenticate(request, username=username, password=password)
            if user is not None:
                djlogin(request, user)
                return JsonResponse({'message':'Login success', 'Login as':user.get_username()})
            else:
                return JsonResponse({'message':'Invalid username or password'})
    return JsonResponse({'message':'Unsupported method!'})

##################################################################################################################################################
#route backend/register : đăng ký v
#POST: gửi tín hiệu đăng ký
from faker import Faker
fake = Faker()
@csrf_exempt
def register(request):
    if request.user.is_authenticated:
        return JsonResponse({'message':'You already login, log out to register new account'})
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repass = request.POST.get('repass')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        company = request.POST.get('company', None)
        if not username:
            return JsonResponse({'message': 'Required username'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'})
        if not first_name:
            return JsonResponse({'message':'Required first_name'})
        if not last_name:
            return JsonResponse({'message':'Required last_name'})
        if not email:
            return JsonResponse({'message':'Required email'})
        if len(password) < 6:
            return JsonResponse({'message':'Password too short'})
        if password != repass:
            return JsonResponse({'message': 'Password not match'})
        
        user = User.objects.create_user(username=username, password=password)
        user.last_name=last_name
        user.first_name=first_name
        user.email=email
        user.save()
        acc = Account.objects.create(user=user, company=company, profile_image = fake.image_url())
        author = AuthorProfile.objects.create(account=acc)
        reader = ReaderProfile.objects.create(account=acc)
        json_data = {
            'message' : 'Register done',
            'name' : acc.user.username,
            'email' : acc.user.email,
            'first_name' : acc.user.first_name,
            'last_name' : acc.user.last_name,
            'company' : acc.company,
            'profile_img_url' : makeUrl(acc.profile_image.url),
            'author_exp' : author.exp,
            'reader_exp' : reader.exp
        }
        return JsonResponse(json_data)
    return JsonResponse({'message':'Unsupported method!'})

##################################################################################################################################################
#route backend/newuniverse: tạo vũ trụ mới v
def makeBool(string):
    if string == 'True':
        return True
    return False
def choisePublic(string):
    if string == 'public' or string == 'subcribe' or string == 'private':
        return string
    return 'public'
@csrf_exempt
def newuniverse(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Login to create new universe'})
    if request.method == "POST":
        user = request.user
        acc = Account.objects.get(user=user)
        auth_pf = AuthorProfile.objects.get(account=acc)
        master = auth_pf
        title = request.POST.get('title')
        if not title:
            return JsonResponse({'message':'Required title'})
        cover_img = fake.image_url()
        world_map = fake.image_url()
        rules = request.POST.get('rules')
        if not rules:
            return JsonResponse({'message':'Required rules'})
        free_add_chapter = makeBool(request.POST.get('free_add_chapter', 'True'))
        public = choisePublic(request.POST.get('public', 'public'))
        uni = Universe.objects.create(master=master, title=title, cover_img=cover_img, world_map=world_map, rules=rules, free_add_chapter=free_add_chapter, public=public)
        uni_info = {
            'message' : 'Create new universe',
            'master' : uni.master.account.user.username,
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'free_add_chapter' : uni.free_add_chapter,
            'public' : uni.public,
            'genres' : {},
            'chapters' : {}
        }
        return JsonResponse(uni_info)
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/universe/{uni_id} v
#GET: Lấy thông tin về vũ trụ
#POST: Thay đổi title và rule
#DELETE: Xóa vũ trụ
@csrf_exempt
def universe(request, uni_id):
    try:
        uni=Universe.objects.get(id=uni_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Universe does not exists'})
    is_master = False
    if request.user.is_authenticated:
        if request.user == uni.master.account.user:
            is_master = True
    if request.method == 'GET':
        gen_dict = {genre.id: genre.name for i, genre in enumerate(uni.genres.all())}
        chapters = Chapter.objects.filter(universe=uni)
        uni_chapter={}
        if chapters.exists():
            uni_chapter = {chapter.id: {chapter.title : chapter.author.pen_name} for i, chapter in enumerate(chapters)}
        uni_info = {
            'message' : 'Get universe info',
            'master' : uni.master.account.user.username,
            'title' : uni.title,
            'cover_img' : makeUrl(uni.cover_image.url),
            'word_map' : makeUrl(uni.world_map.url),
            'rules' : uni.rules,
            'free_add_chapter' : uni.free_add_chapter,
            'public' : uni.public,
            'genres' : gen_dict,
            'chapters' : uni_chapter
        }
        return JsonResponse(uni_info)
    if request.method == 'POST':
        if (not is_master):
            return JsonResponse({'message':'Permission deny!'})
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
        return JsonResponse(uni_info)
    if request.method == 'DELETE':
        if (not is_master):
            return JsonResponse({'message':'Permission deny!'})
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
        return JsonResponse(uni_info)
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/newgenre: tạo thể loại mới v
@csrf_exempt
def newgenre(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Login to add newgenre'})
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', None)
        if not name:
            return JsonResponse({'message':'Required name'})
        if Genre.objects.filter(name=name).exists():
            return JsonResponse({'message':'This genre already exists'})
        genre = Genre.objects.create(name=name, description=description)
        return JsonResponse({'message':'Add genre success', 'genre':{'name':genre.name, 'description':genre.description}})
    return JsonResponse({'message':'Unsupported message'})

##################################################################################################################################################
#route backend/universe/{uni_id}/genre/{genre_id} : thêm hoặc xóa tag thể loại cho vũ trụ v
#PUT: thêm
#DELETE: xóa
@csrf_exempt
def universe_genre(request, uni_id, genre_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Login to change genre for this universe'})
    try:
        uni=Universe.objects.get(id=uni_id)
        genre=Genre.objects.get(id=genre_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Universe or Genre does not exists'})
    is_master = False
    if request.user.is_authenticated:
        if request.user == uni.master.account.user:
            is_master = True
    if request.method == 'PUT':
        if (not is_master):
            return JsonResponse({'message':'Permission deny!'})
        if uni.genres.filter(id=genre_id).exists():
            return JsonResponse({'message':'This universe alredy has the genre'})
        else:
            uni.genres.add(genre)
            return JsonResponse({'message':'Already add '+genre+' to '+uni.title})
    if request.method == 'DELETE':
        if (not is_master):
            return JsonResponse({'message':'Permission deny!'})
        if not uni.genres.filter(id=genre_id).exists():
            return JsonResponse({'message':'This universe dont has the genre'})
        else:
            uni.genres.remove(genre)
            return JsonResponse({'message':'Already remove '+genre+' from '+uni.title})
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/universe/{uni_id}/localmaps: v
#GET: lấy thông tin local_map của vũ trụ
@csrf_exempt
def localmaps(request, uni_id):
    try:
        universe = Universe.objects.get(id=uni_id)
        localMaps = LocalMap.objects.filter(universe=universe)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'Universe does not exists or dont have any local map'})
    if request.method == 'GET':
        localmaps_list = { localmap.local_name : makeUrl(localmap.local_img.url) for i, localmap in enumerate(localMaps)}
        return JsonResponse({'message':'Get localmaps of universe', 'localmaps_list' : localmaps_list})
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/universe/{uni_id}/newlocalmap: thêm localmap mới (đang phát triển)
@csrf_exempt
def newlocalmap(request, uni_id):
    return JsonResponse({'message':'On developping'})

##################################################################################################################################################
#route backend/universe/{uni_id}/localmap/{map_id}: thay đổi localname v
@csrf_exempt
def universe_localmap(request, uni_id, map_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Login to change local name'})
    try:
        universe = Universe.objects.get(id=uni_id)
        local = LocalMap.objects.get(id=map_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'Universe or local map does not exists'})
    is_master = False
    if request.user == universe.master.account.user:
        is_master == True
    if request.method=='POST':
        localname=request.POST.get('localname', local.local_name)
        local.local_name=localname
        local.save()
        return JsonResponse({'message':'Changed local name'})
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/universe/{uni_id}/newchapter v
@csrf_exempt
def newchapter(request, uni_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message':'Login to add new chapter'})
    try:
        uni = Universe.objects.get(id=uni_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'This universe does not exists'})
    if request.method == 'POST':
        acc = Account.objects.get(user=request.user)
        auth = AuthorProfile.objects.get(account=acc)
        title = request.POST.get('title')
        if not title:
            return JsonResponse({'message': 'Required title'})
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
        return JsonResponse(chapter_info)
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/chapter/{chapter_id} v
#GET: lấy thông tin chapter
#POST: Cập nhật
#DELETE: xóa chapter
@csrf_exempt
def chapter(request, chapter_id):
    try:
        chapter=Chapter.objects.get(id=chapter_id)
        paragraphs = Paragraph.objects.filter(chapter = chapter).order_by('ordinal_number')
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Chapter does not exists'})
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
        chapter_info={
            'message' : 'Get chapter info',
            'author' : chapter.author.pen_name,
            'universe' : chapter.universe.title,
            'title' : chapter.title,
            'intro' : chapter.intro,
            'accept' : chapter.accept,
            'paragraph_ids'  : paragraph_ids
        }
        return JsonResponse(chapter_info)
    if request.method == "POST":
        if (not is_master and not is_auth):
            return JsonResponse({'message':'Permission deny'})
        chapter.title = request.POST.get('title', chapter.title)
        chapter.intro = request.POST.get('intro', chapter.intro)
        accept = request.POST.get('accept')
        if accept is not None:
            if(not is_master):
                return JsonResponse({'message':'Only master can accept'})
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
        return JsonResponse({chapter_info})
    if request.method == "DELETE":
        if (not is_master and not is_auth):
            return JsonResponse({'message':'Permission deny'})
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
#route backend/parargaph/{paragraph_id} v
#GET: lấy thông tin paragraph
#POST: Cập nhật
#DELETE: xóa paragraph
@csrf_exempt
def paragraph(request, paragraph_id):
    try:
        para = Paragraph.objects.get(id=paragraph_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'This paragraph does not exists'})
    if request.method == 'GET':
        return JsonResponse({'content' : para.content})
    if request.method == 'POST':
        new_content = request.POST.get('new_content', para.content)
        para.content=new_content
        para.save()
        return JsonResponse({'new_content': para.content})
    if request.method == 'DELETE':
        para.delete()
        return JsonResponse({'message':'Delete paragraph success'})
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/chapter/{chapter_id}/newparagraph: thêm paragraph mới v
@csrf_exempt
def newparagraph(request, chapter_id):
    if request.user.is_authenticated:
        return JsonResponse({'message':'Login to write new paragraph'})
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'Chapter does not exists'})
    auth_user = chapter.author.account.user
    if not auth_user == request.user:
        return JsonResponse({'message':'Permision deny'})
    if request.method == 'POST':
        content=request.POST.get('content')
        if not content:
            return JsonResponse({'message':'Required content'})
        paragraph = Paragraph.objects.create(chapter=chapter, content=content)
        return JsonResponse({'message':'Write paragraph success', 'content':paragraph.content})
    return JsonResponse({'message':'Unsuported method'})

##################################################################################################################################################
#route backend/posts : lấy post theo user.favorite_genre và user->contact->otheruser->post
@csrf_exempt
def posts(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Login to see posts'})
    account = Account.objects.get(user=request.user)
    reader = ReaderProfile.objects.get(account=account)
    has_favorite_tag = True
    favorite_tags = FavoriteGenre.objects.filter(reader=reader)
    if favorite_tags.count() == 0:
        has_favorite_tag=False
    has_contact = True
    contacts = Contact.objects.filter(Query(user_from=request.user) | Query(user_to = request.user), confirm='accepted')
    if contacts.count() == 0:
        has_contact = False
    if has_favorite_tag:
        #object query dùng để lưu truy vấn kiểu: (genres==tag1) | (genres==tag2) ...
        query = Query()
        for tag in favorite_tags:
            q_objects |= Query(genres=tag.genre)
        matching_universes = Universe.objects.filter(q_objects).distinct() #distinct() dùng để loại các vũ trụ trùng lặp trong danh sách
        

##################################################################################################################################################
#route backend/post/{post_id}
#GET: lấy thông tin của bài đăng
#POST: cập nhật bài đăng
#DELETE: xóa bài đăng
@csrf_exempt
def sharedPost(request, post_id):
    if request.method == 'GET':
        return JsonResponse({'message':'Get post info', 'postId': post_id})
    if request.method == 'POST':
        return JsonResponse({'message':'Update post', 'postId': post_id})
    if request.method == 'DELETE':
        return JsonResponse({'message':'Delete post', 'postId': post_id})
    return JsonResponse({'message':"Unsupported method"})

##################################################################################################################################################
#route backend/newpost: tạo post mới
@csrf_exempt
def newPost(request):
    if request.method == 'POST':
        return JsonResponse({'message':'Create new post'})
    return JsonResponse({'message':'Unsupported method'})

##################################################################################################################################################
#route backend/favoritetag:
#GET:lấy các favorite tag
#PUT:chọn favorite tag mới
#POST:thay đổi thứ tự favorite tag
#DELETE:xóa tag
@csrf_exempt
def favorite(request):
    if request.method == 'GET':
        return JsonResponse({'message':'Get all favorite tag'})
    if request.method == 'PUT':
        return JsonResponse({'message':'Add new favorite tag'})
    if request.method == 'POST':
        return JsonResponse({'message':'Update pin number'})
    if request.method == 'DELETE':
        return JsonResponse({'message':'Delete favorite tag'})
    return JsonResponse({'message':'Unsupported method'})

##################################################################################################################################################
#route backend/pinuniverse:

##################################################################################################################################################

##################################################################################################################################################

##################################################################################################################################################

##################################################################################################################################################

##################################################################################################################################################