from django.shortcuts import render, redirect

from .models import Movie
# from user_library.models import WatchedMovie, WatchList, LikedMovie

from django.contrib import messages

# Create your views here.
def list_movie(request):
    try:
        if Movie:
            movies = Movie.objects.all()[:5]
            return render(request, 'movie/list_movie.html', {'movies': movies})
        else:
            return f'No movies found in the database'
    except Exception as e:
        print(f" error :{e}")


def detail_movie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    movie = Movie.objects.get(id=pk)
    return render(request,'movie/detail_movie.html', {'movie': movie})

    # movie type the movie title, use the title to find the movie id and return the Movie id object



    # user_watched_movie = WatchedMovie.objects.filter(user=request.user, movie=movie).first()
    # user_watchlist_movie = WatchList.objects.filter(user=request.user, movie=movie).first()
    # user_liked_movie = LikedMovie.objects.filter(user=request.user, movie=movie).first()