from django.urls import path
from .views import *

urlpatterns = [
    path('account/<int:account_id>', account, name='account_info'),
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('universe/newuniverse', newuniverse, name='newunivese'),
    path('universe/<int:uni_id>', universe, name='universe_info'),
    path('newgenre', newgenre, name='newgenre'),
    path('universe/<int:uni_id>/genre/<int:genre_id>', universe_genre, name='universe_genre'),
    path('universe/<int:uni_id>/newchapter', newchapter, name='newchapter'),
    path('chapter/<int:chapter_id>', chapter, name='chapter_info'),
    path('chapter/<int:chapter_id>/newparagraph', newparagraph, name='newparagraph'),
    path('paragraph/<int:paragraph_id>', paragraph, name='paragraph_info'),
    path('universe/<int:uni_id>/localmaps', localmaps, name='localmaps'),
    path('universe/<int:uni_id>/localmap/<int:map_id>', universe_localmap, name='universe_localmap'),
    path('see/posts', posts, name='see_posts'),
    path('post/<int:post_id>', sharedPost, name='post'),
    path('newpost',newPost, name='newPost'),
    path('favoritetag', favorite, name='favoritetag'),
    path('pinuniverse', pinuniverses, name='pinuniverse'),
    path('see/contacts', seecontacts, name='see_contacts')
]