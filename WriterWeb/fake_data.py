import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WriterWeb.settings")
django.setup()

import random
from faker import Faker
from django.contrib.auth.models import User
from backend.models import Account, Contact, Message, AuthorProfile, ReaderProfile, Genre, Universe, LocalMap, Chapter, Paragraph, PinUniverse, ReadLog, FavoriteGenre, Rating, Comment, Donation, SharedPost
from django.db.models import Q as Query

fake = Faker()

# Hàm tạo dữ liệu ngẫu nhiên cho các bảng
#v
def create_fake_user():
    username = fake.user_name()
    email = fake.email()
    password = username+"@test"
    first_name = fake.first_name()
    last_name = fake.last_name()
    user = User.objects.create_user(username=username, email=email, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    return user
#v
def create_fake_account(user):
    imgurl=fake.image_url()
    while "placekitten.com" in imgurl:
        imgurl = fake.image_url()
    profile_image = imgurl
    profile_name = str(user.username).upper()
    created_at = fake.date_time_this_decade()
    company = fake.company()
    return Account.objects.create(user=user, profile_image=profile_image, created_at=created_at, company = company, profile_name=profile_name)
#v
def create_fake_contact(user_from, user_to):
    if Contact.objects.filter(user_from=user_from, user_to=user_to).exists() or Contact.objects.filter(user_from=user_to, user_to=user_from).exists():
        return False
    created_at = fake.date_time_this_month()
    confirm = random.choice(['waiting', 'accepted', 'rejected'])
    return Contact.objects.create(user_from=user_from, user_to=user_to, created_at=created_at, confirm=confirm)
#v
def create_fake_message(contact):
    content = fake.text()
    timestamp = fake.date_time_this_month()
    is_read = fake.boolean()
    sender = fake.boolean()
    return Message.objects.create(contact=contact, content=content, timestamp=timestamp, is_read=is_read, sender=sender)
#v
def create_fake_author_profile(account):
    exp = fake.random_int(min=0, max=100)
    pen_name = account.user.username.upper()
    return AuthorProfile.objects.create(account=account, exp=exp, pen_name=pen_name)
#v
def create_fake_reader_profile(account):
    exp = fake.random_int(min=0, max=100)
    return ReaderProfile.objects.create(account=account, exp=exp)
#v
def create_fake_genre():
    name = fake.word()
    description = fake.text()
    return Genre.objects.create(name=name, description=description)
#v
def create_fake_universe(master):
    title = fake.word()
    imgurl=fake.image_url()
    while "placekitten.com" in imgurl:
        imgurl = fake.image_url()
    cover_image = imgurl
    imgurl=fake.image_url()
    while "placekitten.com" in imgurl:
        imgurl = fake.image_url()
    world_map = imgurl
    rules = fake.text()
    free_add_chapter = fake.boolean()
    public = random.choice(['public','subcribe','private'])
    universe = Universe.objects.create(master=master, title=title, cover_image=cover_image, world_map=world_map, rules=rules, free_add_chapter=free_add_chapter, public=public)
    for _ in range(random.randint(1, 5)):
        create_fake_local_map(universe)
    return universe
#v
def create_fake_local_map(universe):
    local_name = fake.word()
    imgurl=fake.image_url()
    while "placekitten.com" in imgurl:
        imgurl = fake.image_url()
    local_img = imgurl
    return LocalMap.objects.create(universe=universe, local_name=local_name, local_img=local_img)
#v
def create_fake_chapter(author, universe):
    title = fake.word()
    intro = fake.text()
    accept = random.choice(['wait', 'accepted'])
    chapter = Chapter.objects.create(author=author, universe=universe, title=title, intro=intro, accept=accept)
    create_fake_paragraphs(chapter)
    return chapter
#v
def create_fake_paragraphs(chapter):
    content = fake.text()
    for i in range(10):
        Paragraph.objects.create(ordinal_number = i, chapter = chapter, content=content)
#v
def create_fake_pin_universe(reader, universe):
    pin_number = fake.random_int(min=1, max=10)
    return PinUniverse.objects.create(reader=reader, universe=universe, pin_number=pin_number)
#v
def create_fake_read_log(reader, chapter):
    touch_times = fake.random_int(min=0, max=100)
    memory_tag = fake.word()
    return ReadLog.objects.create(reader=reader, chapter=chapter, touch_times=touch_times, memory_tag=memory_tag)
#v
def create_fake_rating(reader, chapter):
    start = fake.random_int(min=1, max=5)
    complain = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Rating.objects.create(reader=reader, chapter=chapter, start=start, complain=complain, saw=saw)
#v
def create_fake_comment(reader, chapter):
    content = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Comment.objects.create(reader=reader, chapter=chapter, content=content, saw=saw)
#v
def create_fake_donation(reader, chapter):
    cost = fake.random_int(min=1, max=100)
    complain = fake.text()
    saw = fake.random_element(elements=['wait', 'saw'])
    return Donation.objects.create(reader=reader, chapter=chapter, cost=cost, complain=complain, saw=saw)
#v
def create_fake_favorite_genre(reader, genre):
    pin_number = random.randint(1,10)
    return FavoriteGenre.objects.create(genre=genre, reader=reader, pin_number=pin_number)

def create_fake_shared_post(reader, chapter):
    content = fake.text()
    return SharedPost.objects.create(reader=reader, chapter=chapter, content=content)
# Tạo dữ liệu ngẫu nhiên
for _ in range(10):
    create_fake_genre()

for _ in range(10):
    #Tạo account:
    user = create_fake_user()
    account = create_fake_account(user)
    author_profile = create_fake_author_profile(account)
    reader_profile = create_fake_reader_profile(account)
    #Tạo vũ trụ:
    for _ in range(random.randint(1,3)):
        universe = create_fake_universe(author_profile)

all_genres = Genre.objects.all()
all_universes = Universe.objects.all()
all_author = AuthorProfile.objects.all()
all_account = Account.objects.all()
all_reader = ReaderProfile.objects.all()
all_chapter = Chapter.objects.all()

for user in all_account:
    other_users = all_account.exclude(Query(id=user.id))
    for user_to in random.sample(list(other_users), random.randint(0,6)):
        contact = create_fake_contact(user, user_to)
        if contact != False:
            for _ in range(random.randint(0,10)):
                create_fake_message(contact)

for universe in all_universes:
    for i in range(random.randint(1,3)):
        random_auth = random.choice(all_author)
        create_fake_chapter(random_auth, universe)
    random_genres = all_genres.order_by('?')[:random.randint(1,5)]
    universe.genres.set(random_genres)

for reader in all_reader:
    for genre in random.sample(list(all_genres), random.randint(0,5)):
        create_fake_favorite_genre(reader, genre)
    for universe in random.sample(list(all_universes), random.randint(0,10)):
        create_fake_pin_universe(reader, universe)
    for chapter in random.sample(list(all_chapter), random.randint(0,10)):
        create_fake_read_log(reader, chapter)
        create_fake_comment(reader, chapter)
        create_fake_rating(reader, chapter)
        create_fake_donation(reader, chapter)
        create_fake_shared_post(reader, chapter)

for universe in all_universes:
    universe.save()