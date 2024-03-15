from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#Các models liên qua đến người dùng
def user_directory_path(instance, filename):
    #Tạo đường dẫn động để lưu các file của Account
    return f'account_profiles/{instance.user.id}/{filename}'

#Các tài khoản
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    company = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

#Liên hệ, bạn bè
class Contact(models.Model):
    user_from = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts_from')
    user_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts_to')
    created_at = models.DateTimeField(auto_now_add=True)

    #Trạng thái gửi yêu cầu liên hệ hay yêu cầu kết bạn
    STATUS_CHOICES = [
        ('waiting', 'Đang đợi xác nhận'),
        ('accepted', 'Đã đồng ý'),
        ('rejected', 'Từ chối'),
    ]
    confirm = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    
    #Đảm bào cặp [user_from, user_to] là duy nhất
    class Meta:
        unique_together = ['user_from', 'user_to']

#Tin nhắn giữa các liên hệ
class Message(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    #Người đã gửi: true | false tương ứng với Contact.user_from | Contact.user_to
    sender = models.BooleanField()

#Profile khi làm tác giả
class AuthorProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=100, null=True)
    exp = models.IntegerField(default=0)

#Profile khi làm đọc giả
class ReaderProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    exp = models.IntegerField(default=0)


#Các models liên quan đến tác phẩm
#Thể loại
class Genre(models.Model):
    name=models.CharField(max_length=50)
    description = models.TextField(null=True)

#Vũ trụ
def universe_cover_path(instance, filename):
    #Tạo đường dẫn động để lưu ảnh bìa của vũ trụ này
    return f'universe_covers/{instance.id}/{filename}'
def world_map_path(instance, filename):
    #Tạo đường dẫn động để lưu bản đồ thế giới của vũ trụ này
    return f'world_maps/{instance.id}/{filename}'
def local_map_path(instance, filename):
    #Tạo đường dẫn động để lưu bản đồ khu vực của vũ trụ này
    return f'local_maps/{instance.universe.id}/{filename}'

class Universe(models.Model):
    master = models.ForeignKey(AuthorProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to=universe_cover_path, null=True, blank=True)
    world_map = models.ImageField(upload_to=world_map_path, null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    rules = models.TextField()
    #free_add_chapter == True thì có thể thêm chương mới mà không cần master duyệt
    free_add_chapter = models.BooleanField(default=True)
    PUBLICMENT = [
        ('public' , 'Ai cũng có thể xem các chapter tại đây'),
        ('subcribe', 'Chỉ người theo dõi nhìn thấy'),
        ('private' , 'Chỉ những tác giả được phép xem')
    ]
    public = models.CharField(max_length=10, choices=PUBLICMENT, default='public')

#Các bản đồ cục bộ của vữ trụ
class LocalMap(models.Model):
    universe = models.ForeignKey(Universe, on_delete=models.CASCADE)
    local_name = models.CharField(max_length=50)
    local_img = models.ImageField(upload_to=local_map_path, null=True, blank=True)

#Chapter
class Chapter(models.Model):
    author=models.ForeignKey(AuthorProfile, on_delete=models.CASCADE)
    universe = models.ForeignKey(Universe, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    intro = models.TextField()
    ACCEPT = [
        ('wait' , 'Đợi master xác nhận'),
        ('accepted' , 'Đã được xác nhận')
    ]
    accept = models.CharField(max_length=10, choices=ACCEPT, default='wait')

#Paragraph in chapter
class Paragraph(models.Model):
    ordinal_number = models.IntegerField(null=False, default=0)
    chapter=models.ForeignKey(Chapter, on_delete=models.CASCADE)
    content=models.TextField(null=False)


#Các models lưu trữ quá trình đọc của Account
#Ghim để dễ theo dõi
class PinUniverse(models.Model):
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    universe = models.ForeignKey(Universe, on_delete=models.CASCADE)
    #Thứ tự hiển thị trên thanh pin
    pin_number = models.IntegerField(null = False, default = 1)
    class Meta:
        unique_together = ['reader', 'universe']

#Nhật ký đọc
class ReadLog(models.Model):
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    #touch_times tăng lên mỗi khi reader ấn xem chương
    touch_times = models.IntegerField(null=False, default=0)
    #Thẻ ghi nhớ để reader tự đặt (có hoặc không)
    memory_tag = models.CharField(max_length = 50, null = True)

#Thể loại yêu thích
class FavoriteGenre(models.Model):
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    #Thứ tự hiển thị trong bảng ghim của reader
    pin_number = models.IntegerField(null = False, default = 1)


#Các models lưu trữ đánh giá của reader cho tác phẩm
#Đánh giá rating từ 1 đến 5 sao
class Rating(models.Model):
    #Trạng thái hiển thị thông báo đến tác giả của Chapter
    SAW_STATUS_CHOICES = [
        ('wait', 'Đang đợi xem thông báo'),
        ('saw', 'Đã xem thông báo'),
    ]
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    start = models.IntegerField(null=False, default=0)
    complain = models.TextField(null = True)
    saw = models.CharField(max_length=10, choices=SAW_STATUS_CHOICES, default='wait')
    class Meta:
        unique_together = ['reader', 'chapter']

#Comment
class Comment(models.Model):
    SAW_STATUS_CHOICES = [
        ('wait', 'Đang đợi xem thông báo'),
        ('saw', 'Đã xem thông báo'),
    ]
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    content = models.TextField()
    saw = models.CharField(max_length=10, choices=SAW_STATUS_CHOICES, default='wait')

#Donation
class Donation(models.Model):
    SAW_STATUS_CHOICES = [
        ('wait', 'Đang đợi xem thông báo'),
        ('saw', 'Đã xem thông báo'),
    ]
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    cost = models.IntegerField(null=False, default=0)
    complain = models.TextField(null = True)
    saw = models.CharField(max_length=10, choices=SAW_STATUS_CHOICES, default='wait')

#Shared post
class SharedPost(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_DEFAULT, default="DELETED")
    reader = models.ForeignKey(ReaderProfile, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add = True)