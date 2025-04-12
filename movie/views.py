from django.shortcuts import render
from django.contrib import messages
# from django.http import JsonResponse
# from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

from .models import Movie
from user_library.models import Like, WatchList
# from .services import add_movies_from_tmdb
# from api_services.TMDB.fetch_movies import fetch_popular_movies



# def admin_check(user):
#     return user.is_superuser  # or user.is_staff for staff users


def list_movie(request): # , page     ----- was for the custom pagination
    '''retrieve the movies from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    #--- custom pagination----
    # if page == 0:
    #     page = 1  # default page number to 1 if page number is 0
    # page -= 1  # as the first page need to consider taking the id's from 0.

    user_liked_movies = []
    
    try:
        if Movie:            
            # paginator implementation
            paginator = Paginator(Movie.objects.all().order_by('-id'), 20)
            # Get the current page number from the GET request
            page = request.GET.get('page')
            movie_list = paginator.get_page(page)


            # Get the user's watchlist content (movies, series)
            user_watchlist_movies = []
            user_watchlist_movies = WatchList.objects.filter(
                                                user=request.user.id, content_type='movie'
                                                ).values_list('object_id', flat=True)


            # Get the user's like content
            user_liked_movies = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='movie'
                                            ).values_list('object_id', flat=True)

            context = {
                'user_liked_movies': user_liked_movies,
                'movie_list' : movie_list,
                'user_watchlist_movies': user_watchlist_movies, 
                }

            return render(request, 'movie/list_movie.html', context=context)
            
        else:
            return f'No movies found in the database'
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")



def movie_overview(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.
        will pass on with the necessary information such as 'Like' 
    '''
    try:
        if Movie:
        # retrieve the specified movie requested by user
            movie = Movie.objects.get(id=pk)
            # Check if user's like the movie

            # Get the user's watchlist content (movies, series)
            user_watchlist_movies = []
            user_watchlist_movies = WatchList.objects.filter(
                                                user=request.user.id, content_type='movie'
                                                ).values_list('object_id', flat=True)

            user_liked_movie = False
            user_liked_movie = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='movie',
                                            object_id=movie.pk
                                            ).values_list('object_id', flat=True)

            print(f"user_liked :{user_liked_movie}") # debug print

            context = {
                'movie': movie,
                'user_liked_movie': user_liked_movie,
                'user_watchlist_movies': user_watchlist_movies,
                }
            
            return render(request,'movie/detail_movie.html', context=context)
        
        else:
            return f'No movies found in the database'
        
    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
