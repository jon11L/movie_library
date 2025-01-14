from django.shortcuts import render, redirect

from movie.models import Movie
from serie.models import Serie

# Create your views here.
def home(request):

    if Movie:
        movies = Movie.objects.order_by('-id')[:8] # display the amount of movies in the database
        movies_count = Movie.objects.count() # display the amount of movies in the database
    if Serie:
        series = Serie.objects.order_by('-id')[:8] # display the amount of movies in the database
        series_count = Serie.objects.count() # display the amount of movies in the database

    context = {
        'movies': movies,
        'movies_count': movies_count,
        'series_count': series_count,
        'series': series

    }

    return render(request, 'main/home.html', context=context)