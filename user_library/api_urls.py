
from django.urls import path, include
from . import views 

app_name = "user_library"

# including the api route here
urlpatterns = [
    path('list/', views.WatchListListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.WatchListDetailView.as_view(), name='detail'),
]