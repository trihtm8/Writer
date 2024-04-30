from django.urls import path, include
from .views import *

urlpatterns = [
    path('main/<int:key>', personalmain, name='personalmain')
]