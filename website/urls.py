from django.urls import path
from website.views import index

urlpatterns = [
    path('', index, name='index'),
]