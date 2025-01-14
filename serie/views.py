from django.shortcuts import render

# Create your views here.
from .models import Serie, Season, Episode


def list_serie(request):
    try:
        series_data = []
        series = Serie.objects.all()[:24] # retrieve the last 24 series added in the Database

        for serie in series:
            last_season = serie.seasons.order_by('-season_number').first()
            last_episode = (last_season.episodes.order_by('-episode_number').first())

            series_data.append({
                'serie': serie,
                'last_season': last_season,
                'last_episode': last_episode
            })

        context = {
            'series_data': series_data,
        }

        return render(request, 'serie/list_serie.html', context=context)
        
    except Exception as e:
        print(f" error :{e}")
        return render(request, 'serie/list_serie.html', context={'error': str(e)})


def detail_serie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    serie = Serie.objects.get(id=pk)
    return render(request,'serie/detail_serie.html', {'serie': serie})