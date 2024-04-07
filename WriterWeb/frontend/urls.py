from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('check/', include('frontend.checkingurls')),
    path('oops/', oops, name='oops'),
    path('middleware/<int:middlekey>', middleware, name='middleware'),
    path('registerdone', registerdone, name='registerdone'),
]
