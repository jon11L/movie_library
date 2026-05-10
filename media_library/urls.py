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

app_name = "media_library"

from django.urls import path
from . import views 

urlpatterns = [
    # path('list/<str:media_type>', views.media_list, name='list'),
    path('movies', views.media_list, {'media_type':'movies'} ,name='movies'),
    path('series', views.media_list, {'media_type':'series'} ,name='series'),
    path('documentaries', views.media_list, {'media_type':'documentaries'} ,name='documentaries'),
    path('short-films', views.media_list, {'media_type': 'short-films'}, name='short-films'),
    path('animes', views.media_list, {'media_type': 'animes'}, name='animes'),
    
    path('detail/<slug:slug>', views.media_detail, name='detail'),
    path('season/<int:season_id>', views.load_season_data, name='season_data'),

]