
from django.urls import path, include
from . import views 

app_name = "serie"

# including the api route here
urlpatterns = [
    path('list/', views.SerieListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.SerieDetailView.as_view(), name='detail'),
]