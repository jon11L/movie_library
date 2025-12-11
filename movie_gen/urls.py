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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
# from . import settings

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse


# a single view to return a list of different api endpoint available
@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        # "register": reverse("register", request=request, format=format),
        "token-auth": reverse("token_auth", request=request, format=format),
        # "api-auth": reverse("api_auth", request=request, format=format),
        "movie-list": reverse("api_movie:list", request=request, format=format),
        "movie-detail": reverse("api_movie:detail", kwargs={"pk": 50}, request=request, format=format),
        "serie-list": reverse("api_serie:list", request=request, format=format),
        "serie-detail": reverse("api_serie:detail", kwargs={"pk": 50}, request=request, format=format),
        "watchlist-list": reverse("api_watchlist:list", request=request, format=format),
        "watchlist-detail": reverse("api_watchlist:detail", kwargs={"pk": 80}, request=request, format=format),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('user/', include('user.urls', namespace='user')),
    path('movie/', include('movie.urls', namespace='movie')),
    path('serie/', include('serie.urls', namespace='serie')),
    path('library/', include('user_library.urls', namespace='user_library')),
    path('search/', include('search.urls', namespace='search')),
    path('comment/', include('comment.urls', namespace='comment')),

    # API rest routes
    path('api/', api_root, name='api_root'),
    path('api-auth/', include('rest_framework.urls'), name="api_auth"), #/login or  for the browsable API /logout
    path('api-token-auth/', obtain_auth_token, name='token_auth'), #create a token for users when posting their cred. to this url. POST {username, password}
    path('api/v1/movie/', include('movie.api_urls', namespace='api_movie')),
    path('api/v1/serie/', include('serie.api_urls', namespace='api_serie')),
    path('api/v1/user_library/', include('user_library.api_urls', namespace='api_watchlist')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Static files (CSS/JS) - Only needed if testing with Gunicorn locally
    # runserver serves these automatically, but Gunicorn doesn't
