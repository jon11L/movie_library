from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Serie
from user_library.models import Like
# from .services import add_series_from_tmdb
# from api_services.TMDB.fetch_series import fetch_popular_series


def list_serie(request):
    '''retrieve the series from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    try:
        if Serie:
            series_data = []
            series = Serie.objects.all().order_by('-id')

            # load the extra information of a series from Season and Episode 
            for serie in series:
                last_season = serie.seasons.order_by('-season_number').first()

                if last_season:
                    last_episode = last_season.episodes.order_by('-episode_number').first() # issue comes from here

                # Series_data contain the serie and Season,Episode information 
                series_data.append({
                    'serie': serie,
                    'last_season': last_season,
                    'last_episode': last_episode
                })

            # paginator implementation
            p = Paginator(series_data, 20)
            page = request.GET.get('page')
            serie_list = p.get_page(page)

            # Get the user's like content
            user_liked_series = []
            user_liked_series = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='serie'
                                            ).values_list('object_id', flat=True)

            context = {
                'user_liked_series': user_liked_series,
                'serie_list' : serie_list,
            }

            return render(request, 'serie/list_serie.html', context=context)
        
        else:
            return f'No series found in the database'
        
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :{e}")



def serie_overview(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    try:
        if Serie:
        # retrieve the specified serie requested by user
            serie = Serie.objects.get(id=pk)

            # Check if user's like the serie
            user_liked_serie = False
            user_liked_serie = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='serie',
                                            object_id=serie.pk
                                            ).values_list('object_id', flat=True)

            print(f"user_liked :{user_liked_serie}") # debug print

            context = {
                'serie': serie,
                'user_liked_serie': user_liked_serie

                }
            
            return render(request,'serie/detail_serie.html', context=context)
        
        else:
            return f'No series found in the database'
        

    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
