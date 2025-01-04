from django.shortcuts import render

from .models import Movie
# from user_library.models import WatchedMovie, WatchList, LikedMovie

# Create your views here.
def list_movie(request):
    if Movie:
      movies = Movie.objects.all()[:5]
    return render(request, 'movie/list_movie.html', {'movies': movies})