from django.urls import path
from website.views import index, login, predict, logout, register, download_template

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('predict/', predict, name='predict'),
    path('download_template/', download_template, name='download_template'),
]