from django.shortcuts import render, redirect

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like

# Create your views here.
def home(request):

    # Check if they are Movie datas and display them if so
    if Movie:
        movies = Movie.objects.order_by('-id')[:8] # display the amount of movies in the database
        movies_count = Movie.objects.count() # display the amount of movies in the database
    if Serie:
        series = Serie.objects.order_by('-id')[:8] # display the amount of movies in the database
        series_count = Serie.objects.count() # display the amount of movies in the database

        # Get the user's like content 
        user_liked_movies = []
        user_liked_movies = Like.objects.filter(
        user=request.user.id, content_type='movie'
        ).values_list('object_id', flat=True)
        print(f"\n user liked:\n\n{user_liked_movies}\n")




    context = {
        'movies': movies,
        'movies_count': movies_count,
        'series_count': series_count,
        'series': series,
        'user_liked_movies': user_liked_movies
        

    }

    return render(request, 'main/home.html', context=context)