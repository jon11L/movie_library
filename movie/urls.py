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

app_name = "movie"

from django.urls import path
from . import views 

urlpatterns = [
    path('list_movie/', views.list_movie, name='list_movie'),
    # path('list_movie/<int:page>', views.list_movie, name='list_movie'), # was for custom pagination
    path('movie_overview/<int:pk>', views.movie_overview, name='movie_overview'),

    # path('edit_movie/<int:pk>', views.edit_movie, name='edit_movie'),
    # path('delete_movie/<int:pk>', views.delete_movie, name='delete_movie'),
    # path('search_movie', views.search_movie, name='search_movie'),

]