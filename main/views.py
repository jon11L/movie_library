from django.shortcuts import render, redirect

from movie.models import Movie
# Create your views here.
def home(request):

    if Movie:
        movies_count = Movie.objects.count() # display the amount of movies in the database

        # if there are more than 5 movies, display only the first 5 movies
        # last_movies = Movie.objects.get(pk=[5:]).order_by('
        # last_movies = Movie.objects.

    return render(request, 'main/home.html', {'movies_count': movies_count})