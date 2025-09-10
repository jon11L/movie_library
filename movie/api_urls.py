
from django.urls import path, include
from . import views 

app_name = "movie"

# including the api route here
urlpatterns = [
    path('list/', views.MovieListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.MovieDetailView.as_view(), name='detail'),
]