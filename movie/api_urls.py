
app_name = "movie"

from django.urls import path, include
from . import views 


# including the api route here
urlpatterns = [
    # path('', include(router.urls)),
    path('list/', views.MovieListView.as_view()),
    path('detail/<int:pk>/', views.MovieDetailView.as_view()),
]