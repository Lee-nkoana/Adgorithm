from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path('platforms/', views.platforms, name="platforms"), 
    path('profile/', views.profile, name="profile"),
]