from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
# from django.contrib.auth.decorators import user_passes_test

import datetime
import random
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

        def pick_content(list_sample):
            '''Takes a list sample from the queryset or list given'''
            return random.sample(list(list_sample), 6) 
            

        # to display movies & series that are coming soon or recently released
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)  # 7 days ago
        bi_week_later = today + datetime.timedelta(days=14)  # 14 days later
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday of the current week
        week_end = week_start + datetime.timedelta(days=6)  # Sunday of the current week
        fortnight_ago = today - datetime.timedelta(days=15)  # 15 days ago
        month_ago = today - datetime.timedelta(days=30)  # 30 days ago

        movies = Movie.objects.all()
        series = Serie.objects.all()
        

        recently_released_movies = movies.filter(release_date__range=(week_ago, today)).exclude(length__range=(0, 45))  # retrieve the 10 latest content added
        print(f"\n recently released movies: {len(recently_released_movies)}\n") # debug print
        recently_released_movies = pick_content(recently_released_movies)  # retrieve 8 random movies from the last 30 days

        coming_soon_movies = movies.filter(release_date__range=(today, bi_week_later)).exclude(length__range=(0, 45))  # retrieve the movies coming soon.
        print(f"\n coming soon movies: {len(coming_soon_movies)}\n") # debug print
        coming_soon_movies = pick_content(coming_soon_movies) 


        random_pick_movies = random.sample(list(movies.exclude(length__range=(0, 45))), 6)  # retrieve 8 random movies from the last 30 days
        print(f"\n random pick movies:\n\n{random_pick_movies}\n") # debug print


        # series = Serie.objects.filter(last_air_date__range=(week_start, week_end))[:8] 
        coming_back_series = series.filter(last_air_date__range=(fortnight_ago, bi_week_later))
        print(f"\n coming back series: {len(coming_back_series)}\n") # debug print
        coming_back_series = pick_content(coming_back_series)  # retrieve 8 random movies from the last 30 days

        coming_up_series = series.filter(first_air_date__range=(fortnight_ago, bi_week_later))  # retrieve the 8 latest content added
        print(f"\n coming up series: {len(coming_up_series)}\n") # debug print
        coming_up_series = pick_content(coming_up_series)  # retrieve 8 random movies from the last 30 days
        

        movies_count = movies.count() # display the amount of movies in the database
        series_count = series.count() 

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
        
        # print(f"\n user liked:\n\n{user_liked_movies}\n") # debug print
        # print(f"\n user liked:\n\n{user_liked_series}\n") # debug print

        context = {
            'movies': recently_released_movies,
            'coming_soon': coming_soon_movies,
            'random_movies': random_pick_movies,
            'series': coming_back_series,
            'coming_up_series': coming_up_series,
            'movies_count': movies_count,
            'series_count': series_count,
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



