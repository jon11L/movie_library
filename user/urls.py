"""
URL configuration for movie_gen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


app_name = 'user'

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    
    path('profile/<int:pk>', views.profile_page, name='profile_page'),
    path('profile/<int:pk>/update_profile', views.update_profile, name='update_profile'),
    path('profile/<int:pk>/update_user_name', views.update_user, name='update_user_name'),
    path('profile/<int:pk>/update_user_pw', views.update_password, name='update_user_pw'),

    path('toggle_watchlist_privacy', views.toggle_watchlist_privacy, name='toggle_watchlist_privacy'),

]
