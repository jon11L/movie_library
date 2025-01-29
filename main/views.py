from django.shortcuts import render, redirect
from django.contrib import messages

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like

# Create your views here.
def home(request):

    # Check if they are Movie datas and display them if so
    try:
        movies = Movie.objects.order_by('-id')[:8] # retrieve the latest 8 content added 
        movies_count = Movie.objects.count() # display the amount of movies in the database
        series = Serie.objects.order_by('-id')[:8] 
        series_count = Serie.objects.count() 


        # Get the user's like content (movies, series)
        user_liked_movies = []
        user_liked_movies = Like.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_liked_series = []
        user_liked_series = Like.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)
        
        print(f"\n user liked:\n\n{user_liked_movies}\n")
        print(f"\n user liked:\n\n{user_liked_series}\n")

        context = {
            'movies': movies,
            'movies_count': movies_count,
            'series_count': series_count,
            'series': series,
            'user_liked_movies': user_liked_movies,
            'user_liked_series': user_liked_series

        }

        return render(request, 'main/home.html', context=context)
    
    except Exception as e:
        print(f"An error occurred while loading the homepage: {e}\n")
        messages.error(request, "An error occurred while loading the page.")
        return redirect(to='main:home')