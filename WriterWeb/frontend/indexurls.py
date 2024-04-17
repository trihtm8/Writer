from django.urls import path, include
from .views import *

urlpatterns = [
    path('header/<int:key>', indexheaderroute, name='header'),
    path('left/<int:key>', indexleftroute, name='indexleft'),
    path('main/<int:key>', indexmainroute, name='indexmain'),
    path('right/<int:key>', indexrightroute, name='indexright')
]