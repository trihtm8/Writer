import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WriterWeb.settings")
django.setup()

import random
from faker import Faker
from django.contrib.auth.models import User
from backend.models import Account, Contact, Message, AuthorProfile, ReaderProfile, Genre, Universe, LocalMap, Chapter, PinUniverse, ReadLog, FavoriteGenre, Rating, Comment, Donation

fake = Faker()

# Hàm tạo dữ liệu ngẫu nhiên cho các bảng

def create_fake_user():
    username = fake.user_name()
    email = fake.email()
    password = fake.password()
    user = User.objects.create_user(username=username, email=email, password=password)
    return user

def create_fake_account(user):
    profile_image = fake.image_url()
    created_at = fake.date_time_this_decade()
    return Account.objects.create(user=user, profile_image=profile_image, created_at=created_at)

def create_fake_contact():
    user_from = create_fake_account(create_fake_user())
    user_to = create_fake_account(create_fake_user())
    created_at = fake.date_time_this_month()
    confirm = random.choice(['waiting', 'accepted', 'rejected'])
    return Contact.objects.create(user_from=user_from, user_to=user_to, created_at=created_at, confirm=confirm)

def create_fake_message(contact):
    content = fake.text()
    timestamp = fake.date_time_this_month()
    is_read = fake.boolean()
    sender = fake.boolean()
    return Message.objects.create(contact=contact, content=content, timestamp=timestamp, is_read=is_read, sender=sender)

def create_fake_author_profile(account):
    exp = fake.random_int(min=0, max=100)
    return AuthorProfile.objects.create(account=account, exp=exp)

def create_fake_reader_profile(account):
    exp = fake.random_int(min=0, max=100)
    return ReaderProfile.objects.create(account=account, exp=exp)

def create_fake_genre():
    name = fake.word()
    description = fake.text()
    return Genre.objects.create(name=name, description=description)

def create_fake_universe():
    title = fake.word()
    cover_image = fake.image_url()
    world_map = fake.image_url()
    rules = fake.text()
    return Universe.objects.create(title=title, cover_image=cover_image, world_map=world_map, rules=rules)

def create_fake_local_map(universe):
    local_name = fake.word()
    local_img = fake.image_url()
    return LocalMap.objects.create(universe=universe, local_name=local_name, local_img=local_img)

def create_fake_chapter(universe):
    title = fake.word()
    intro = fake.text()
    content = fake.text()
    return Chapter.objects.create(universe=universe, title=title, intro=intro, content=content)

def create_fake_pin_universe(reader):
    universe = create_fake_universe()
    pin_number = fake.random_int(min=1, max=10)
    return PinUniverse.objects.create(reader=reader, universe=universe, pin_number=pin_number)

def create_fake_read_log(reader):
    chapter = create_fake_chapter(create_fake_universe())
    touch_times = fake.random_int(min=0, max=100)
    memory_tag = fake.word()
    return ReadLog.objects.create(reader=reader, chapter=chapter, touch_times=touch_times, memory_tag=memory_tag)

def create_fake_favorite_genre(reader):
    genre = create_fake_genre()
    pin_number = fake.random_int(min=1, max=10)
    return FavoriteGenre.objects.create(reader=reader, genre=genre, pin_number=pin_number)

def create_fake_rating(reader):
    chapter = create_fake_chapter(create_fake_universe())
    start = fake.random_int(min=1, max=5)
    complain = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Rating.objects.create(reader=reader, chapter=chapter, start=start, complain=complain, saw=saw)

def create_fake_comment(reader):
    chapter = create_fake_chapter(create_fake_universe())
    content = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Comment.objects.create(reader=reader, chapter=chapter, content=content, saw=saw)

def create_fake_donation(reader):
    chapter = create_fake_chapter(create_fake_universe())
    cost = fake.random_int(min=1, max=100)
    complain = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Donation.objects.create(reader=reader, chapter=chapter, cost=cost, complain=complain, saw=saw)

# Tạo dữ liệu ngẫu nhiên

for _ in range(5):
    user = create_fake_user()
    account = create_fake_account(user)
    contact = create_fake_contact()
    message = create_fake_message(contact)
    author_profile = create_fake_author_profile(account)
    reader_profile = create_fake_reader_profile(account)
    genre = create_fake_genre()
    universe = create_fake_universe()
    local_map = create_fake_local_map(universe)
    chapter = create_fake_chapter(universe)
    pin_universe = create_fake_pin_universe(reader_profile)
    read_log = create_fake_read_log(reader_profile)
    favorite_genre = create_fake_favorite_genre(reader_profile)
    rating = create_fake_rating(reader_profile)
    comment = create_fake_comment(reader_profile)
    donation = create_fake_donation(reader_profile)

all_genres = Genre.objects.all()
all_universes = Universe.objects.all()

for universe in all_universes:
    # Lấy ngẫu nhiên một số lượng thể loại
    random_genres = all_genres.order_by('?')[:random.randint(1,5)]
    
    # Thêm thể loại vào vũ trụ
    universe.genres.set(random_genres)

for universe in all_universes:
    universe.save()