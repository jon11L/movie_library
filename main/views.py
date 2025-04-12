from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

# from api_services.TMDB.base_client import TMDBClient
# from api_services.TMDB.fetch_movies import get_movie_data

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like , WatchList


def admin_check(user):
    return user.is_superuser  # or user.is_staff for staff users


def home(request):
    '''
    Homepage landing, with display of some latest content (Movies and Series)
    '''
    # Check if they are Movie datas and display them if so
    try:
        movies = Movie.objects.order_by('-release_date')[:8] # retrieve the latest 8 content added 
        series = Serie.objects.order_by('-id')[:8] 
        
        movies_count = Movie.objects.count() # display the amount of movies in the database
        series_count = Serie.objects.count() 

        # Get the user's watchlist content (movies, series)
        user_watchlist_movies = []
        user_watchlist_movies = WatchList.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_watchlist_series = []
        user_watchlist_series = WatchList.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)

        print(f"\n user has in watchlist:\n\n{user_watchlist_movies}\n") # debug print
        print(f"\n user has in watchlist:\n\n{user_watchlist_series}\n") # debug print

        # Get the user's like content (movies, series)
        user_liked_movies = []
        user_liked_movies = Like.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_liked_series = []
        user_liked_series = Like.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)
        
        print(f"\n user liked:\n\n{user_liked_movies}\n") # debug print
        print(f"\n user liked:\n\n{user_liked_series}\n") # debug print

        context = {
            'movies': movies,
            'movies_count': movies_count,
            'series_count': series_count,
            'series': series,
            'user_liked_movies': user_liked_movies,
            'user_liked_series': user_liked_series,
            'user_watchlist_movies': user_watchlist_movies,
            'user_watchlist_series': user_watchlist_series,


        }

        return render(request, 'main/home.html', context=context)
    
    except Exception as e:
        print(f"An error occurred while loading the homepage: {e}\n")
        messages.error(request, "An error occurred while loading the page.")
        return redirect(to='main:home')


def about_page(request):
    return render(request, 'main/about.html')



