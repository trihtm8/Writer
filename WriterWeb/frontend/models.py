from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator

class Key(models.Model):
    key = models.IntegerField(validators=[MinValueValidator(10000), MaxValueValidator(99999)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    touch = models.DateTimeField(auto_now=True)

class Urls(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    middlekey = models.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(999999)])
    url = models.TextField()
    type = models.TextField()