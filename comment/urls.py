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

app_name = 'comment'

urlpatterns = [
    # path('show_comment/<int:pk>/', views.show_comment, name='show_comment'),
    path('create', views.create_comment, name='create'),
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('edit/<int:pk>/', views.edit_comment, name='edit'),

]
