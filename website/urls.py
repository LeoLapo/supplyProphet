from django.urls import path
from website.views import index, login, predict, logout, register, download_template, contact, prediction_list,save_data_view,get_data_view,download_file_view, upload_file_view
urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('contact/', contact, name='contact'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('predict/', predict, name='predict'),
    path('download_template/', download_template, name='download_template'),
    path('prediction_list/', prediction_list, name='prediction_list'),

    path('save-data/', save_data_view, name='save_data'),
    path('get-data/', get_data_view, name='get_data'),
    path('upload-file/', upload_file_view, name='upload_file'),
    path('download-file/', download_file_view, name='download_file'),
]