# adgoMain/urls.py
# Defines app specific routes
from django.urls import path
from . import views

app_name = 'adgoMain'

urlpatterns = [
    path('auth/', views.youtube_auth, name='youtube_auth'),
    path('stats/', views.channel_stats, name='channel_stats'),
]