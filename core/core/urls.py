from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView  

from landing.views import ( index,about, services, blog, news_list, news_create, contact, login_view, favorite, map,  dashboard, my_properties, chat_support, hidden_listings, 
settings_view, profile_view, doacoes, musicas
)


urlpatterns = [
    path('admin/', admin.site.urls),
  
    # Auth
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
     path('i18n/', include('django.conf.urls.i18n')),

    # paginas Nav
    path('', index, name='index'),  
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    path('blog/', blog, name='blog'),
    path("news/", news_list, name="news-list"),
    path("news/create/", news_create, name="news-create"),
    path('doacoes_all/', doacoes, name='doacoes'),
    path('musicas/', musicas, name='musicas'),
    path('contact/', contact, name='contact'),
    

    # Menu Usuario Logueado

    path('favorite/get', favorite, name='favorite'),      
    path('dashboard/', dashboard, name='dashboard'),
    path('properties/', my_properties, name='my_properties'),
    path('chat-support/', chat_support, name='chat_support'),
    path('favorites/', favorite, name='favorites'),
    path('hidden-listings/', hidden_listings, name='hidden_listings'),
    path('map/', map, name='map'),
    path('settings/', settings_view, name='settings'),
    path('profile/', profile_view, name='profile'),
]

