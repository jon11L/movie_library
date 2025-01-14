from django.shortcuts import render

from.models import LikedMovie
from user.models import User#, Profile
from movie.models import Movie

# Create your views here.
def liked_movies(request, pk):
    '''retrieve the user's liked mvoie list from the database and display them in the template'''


    # if request.method == "GET":

    if request.user.is_authenticated:
    # fetch the profile being requested
        user = User.objects.get(id=pk)
        
        liked_movies = LikedMovie.objects.filter(user=pk)

        # get the movie objects
        movies = [liked_movie.movie for liked_movie in liked_movies]

        context = {
            'liked_movies': liked_movies,
            'user': user,
            'movies': movies
        }
        return render(request, 'user_library/liked_movies.html', context=context)