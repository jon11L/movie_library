from django.shortcuts import render
from django.contrib import messages

from .models import Serie
from user_library.models import Like


def list_serie(request):
    '''retrieve the series from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    try:
        if Serie:
            series_data = []
            series = Serie.objects.order_by('-id')[:24] # retrieve the last 24 series added in the Database

            # load the extra information of a series from Season and Episode 
            for serie in series:
                last_season = serie.seasons.order_by('-season_number').first()
                last_episode = last_season.episodes.order_by('-episode_number').first()

                # Series_data contain the serie and Season,Episode information 
                series_data.append({
                    'serie': serie,
                    'last_season': last_season,
                    'last_episode': last_episode
                })

            print(f"Series_data:\n {series_data}\n") # debug print 

            # Get the user's like content
            user_liked_series = []
            user_liked_series = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='serie'
                                            ).values_list('object_id', flat=True)

            context = {
                'series_data': series_data,
                'user_liked_series': user_liked_series
            }

            return render(request, 'serie/list_serie.html', context=context)
        
        else:
            return f'No series found in the database'
        
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :{e}")



def detail_serie(request, pk):
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