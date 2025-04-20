from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

# from django.contrib.auth.decorators import user_passes_test
import datetime
import random

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like , WatchList
from user.models import User


def admin_check(user):
    return user.is_superuser  # or user.is_staff for staff users


# def home(request, *args, **kwargs):
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
        yesterday = today - datetime.timedelta(days=1)  # yesterday
        week_ago = today - datetime.timedelta(days=7)  # 7 days ago
        bi_week_later = today + datetime.timedelta(days=14)  # 14 days later
        fortnight_ago = today - datetime.timedelta(days=14)  # 2 weeks ago
        month_ago = today - datetime.timedelta(days=30)  # 30 days ago
        week_start = today - datetime.timedelta(days=today.weekday())  # Monday of the current week
        week_end = week_start + datetime.timedelta(days=6)  # Sunday of the current week

        movies = Movie.objects.all()
        series = Serie.objects.all()
        
        recently_released_movies = movies.filter(release_date__range=(fortnight_ago, yesterday)).exclude(length__range=(0, 45))  # retrieve the 10 latest content added
        print(f"\n recently released movies: {len(recently_released_movies)}\n") # debug print
        recently_released_movies = pick_content(recently_released_movies)  # retrieve 6 random movies from the last week

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
        
        # random_pick_series = random.sample(list(series.exclude(length__range=(0, 45))), 6)  # retrieve 8 random movies from the last 30 days
        random_pick_series = pick_content(series)  # retrieve 8 random movies from the last 30 days
        print(f"\n random pick series:\n\n{random_pick_series}\n") # debug print

        movies_count = movies.count() # display the amount of movies in the database
        series_count = series.count() 

        # ------ Get the user's watchlist content (movies, series)  -------
        user_watchlist_movies = []
        user_watchlist_movies = WatchList.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_watchlist_series = []
        user_watchlist_series = WatchList.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)

        # print(f"\n user has in watchlist:\nMovie: {user_watchlist_movies}") # debug print
        # print(f"Serie: {user_watchlist_series}\n") # debug print

        # ----- Get the user's like content (movies, series)  -----
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


        user = User.objects.get(id=request.user.id)
        print(f"\n user:\n\n{user}\n") # debug print
        watchlist = WatchList.objects.filter(user=request.user.id)
        print(f"\n user watchlist:\n\n{watchlist[:3]}\n") # debug print

        watchlist_content = [] # intialize the list of watchlist instances 
        for item in watchlist:
            if item.content_type == "movie":
                try:
                    movie = Movie.objects.get(id=item.object_id)
                    watchlist_content.append({'content_type': item.content_type, 'object': movie, 'added_on': item.created_on.strftime("%d %B %Y")})
                    # print(f"movie: {movie}\n") #debug print
                except Movie.DoesNotExist:
                    continue

            elif item.content_type == "serie":
                try:
                    serie = Serie.objects.get(id=item.object_id)
                    watchlist_content.append({'content_type': item.content_type, 'object': serie, 'added_on': item.created_on.strftime("%d %B %Y")})
                    # print(f"serie: {serie}\n") #debug print
                except Serie.DoesNotExist:
                    continue


        watchlist_content = pick_content(watchlist_content)  # retrieve 6 random content from the user's watchlist

        context = {
            'movies': recently_released_movies,
            'coming_soon': coming_soon_movies,
            'random_movies': random_pick_movies,
            'series': coming_back_series,
            'coming_up_series': coming_up_series,
            'random_series': random_pick_series,
            'movies_count': movies_count,
            'series_count': series_count,
            'watchlist_content': watchlist_content,

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



def show_documentaries(request):
    '''
    Display the documentaries available in the database
    '''
    documentaries = []

    try:
        # Check if they are Movie datas and display them if so
        movies = Movie.objects.filter(genre__icontains = "documentary")
        series = Serie.objects.filter(genre__icontains = "documentary")
        print(f"\n documentaries movies: {len(movies)}\n") # debug print
        print(f"\n documentaries series: {len(series)}\n") # debug print
        
        # combine movies and series into a single list or object to pass in paginator
        for movie in movies:
                documentaries.append({
                    'object': movie,
                    'type': 'movie',
                })

        for serie in series:
            documentaries.append({
                'object': serie,
                'type': 'serie',
            })


        # Sort the documentaries by title (ascending order)
        documentaries = sorted(documentaries, key=lambda x: x['object'].title, reverse=False)  # sort by release date

        # -- paginate over the results --
        paginator = Paginator(documentaries, 24)
        page_number = request.GET.get('page')
        page_object = paginator.get_page(page_number)
        print(f"List content: {page_object}")

        # Get the user's like content (movies, series)
        user_liked_movies = []
        user_liked_movies = Like.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_liked_series = []
        user_liked_series = Like.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)
        
        # Get the user's watchlist content (movies, series)
        user_watchlist_movies = []
        user_watchlist_movies = WatchList.objects.filter(
                                            user=request.user.id, content_type='movie'
                                            ).values_list('object_id', flat=True)

        user_watchlist_series = []
        user_watchlist_series = WatchList.objects.filter(
                                            user=request.user.id, content_type='serie'
                                            ).values_list('object_id', flat=True)


        context = {
            'movies': movies,
            'series': series,
            'list_content': page_object,
            'user_liked_movies': user_liked_movies,
            'user_liked_series': user_liked_series,
            'user_watchlist_movies': user_watchlist_movies,
            'user_watchlist_series': user_watchlist_series,
        }

        return render(request, 'main/documentaries.html', context=context)
    
    except Exception as e:
        print(f"An error occurred while loading the documentaries page: {e}\n")
        messages.error(request, f"An error occurred while loading the page. {e}")
        return redirect(to='main:home')