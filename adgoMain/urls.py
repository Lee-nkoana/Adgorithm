# adgoMain/urls.py
# Defines app specific routes
from django.urls import path
from . import views

# app_name = 'adgoMain'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # path('auth/', views.youtube_auth, name='youtube_auth'),
    # path('stats/', views.channel_stats, name='channel_stats'),
    path('auth/start/', views.youtube_auth_start, name='youtube_auth_start'),
    path('oauth2callback/', views.youtube_auth_callback, name='youtube_auth_callback'),
    path('stats/', views.channel_stats, name='channel_stats'),

    
]