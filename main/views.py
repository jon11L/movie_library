from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

from api_services.TMDB.base_client import TMDBClient
from api_services.TMDB.fetch_movies import get_movie_details

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like


def admin_check(user):
    return user.is_superuser  # or user.is_staff for staff users

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
    



# Find a way to authorize the only for admin  --- Below are test functions for the API calls with TMDB

@user_passes_test(admin_check, login_url="user:login", redirect_field_name="main/home")
def get_tmdb_access(request):
    '''Make the first call to TMDB api to get the read access to the apis/datas.
    If user is not admin, will be redirected to login page"
    '''

    if request.method == 'GET':
        client = TMDBClient()
        client_access = client.get_authorization()

        if client_access:
            messages.success(request, "request to read access TMDB api was successful")
            # return render(request, 'main/tmdb_access.html', {'access_token': access})
            return JsonResponse(client_access)
        
        else:
            messages.error(request, "The request to read access TMDB api was not successful.")
            return redirect(to='main:home')



# function to test API. and data retrieval
def search_movie(request):
    tmdb_id =  '650'  # Default search for testing
    # client = TMDBClient()
    movie_data = get_movie_details(tmdb_id)
    # credit_data = client.get_movie_credits(query)
    return JsonResponse({
        'data': movie_data
    })

