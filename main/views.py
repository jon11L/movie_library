from django.shortcuts import render, redirect

from movie.models import Movie
# Create your views here.
def home(request):

    if Movie:
        movies_count = Movie.objects.count() # display the amount of movies in the database

    return render(request, 'main/home.html', {'movies_count': movies_count})