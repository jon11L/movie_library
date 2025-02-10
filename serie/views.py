from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Serie
from user_library.models import Like
from .services import add_series_from_tmdb
from api_services.TMDB.fetch_series import fetch_popular_series


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

            print(f"Series_data:\n {series_data}\n") # debug print 

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




def import_serie(request, tmdb_id):
    '''Import a movie in making a request to TMDB api and store it in the database'''
    print(f"request importing a new serie")
    try:
        if request.method == 'GET' and request.user.is_superuser:

            try:
                # check if the movie is already in our database
                exisiting_serie = Serie.objects.get(tmdb_id=tmdb_id)
                print(f"Serie already exists: serie {exisiting_serie.id}: {exisiting_serie.title}")
                return JsonResponse({
                    'status': 'already exists in DB', 
                    'tmdb_id': exisiting_serie.tmdb_id, 
                    'serie_id': exisiting_serie.id,
                    'title': exisiting_serie.title
                }, status=200)
            
            # if the movie is not then we try to fetch it.
            except Serie.DoesNotExist:

                result = add_series_from_tmdb(tmdb_id)

                # Determine appropriate HTTP status code
                status_code = {
                    'added': 201,
                    'exists': 200,
                    'error': 404
                }.get(result['status'], 400)

                return JsonResponse(result, status=status_code)
        else:
            print(f"Unauthorized access to 'import_serie' page.")
            messages.error(request, "You are not authorized to import series")
            return redirect('main:home')

    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)
    


def bulk_import_series(request):
    """
    Bulk import strategy:
    1. Fetch popular series
    3. Check if already in database / if so, pass.
    3.  loop through each serie to query their data 
    4. Import new series 
    """
    try:
        if request.user.is_superuser:
            
            page = 17 # for now the page is decided here and line 153 to choose the amount (only temporary)
            while True:
                print(f"request importing list popular series page: {page}\n") # debug print
                popular_series = fetch_popular_series(page)

                if not popular_series:
                    print(f" The query could not fetch a list of popular series, check the url.")  # debug print
                    return JsonResponse({'message': 'Bulk import failed, check Url'}, status=404)
                
                print("\n Looping through the list of popular series and pass the Ids to get the datas.\n")
                for tmdb_serie in popular_series['results']:
                    tmdb_id = tmdb_serie['id']
                    print(f" passing tmdb_id: {tmdb_id}") # debug print

                    # Check if serie exists
                    if not Serie.objects.filter(tmdb_id=tmdb_id).exists():
                        try:
                            add_series_from_tmdb(tmdb_id)
                            print(f"Imported serie: {tmdb_serie['name']}\n")  # not sure it is imported if already exist
                        except Exception as e:
                            print(f"Error importing {tmdb_serie['name']}: {e}")
                    else:
                        print(f"{tmdb_serie['name']} already exists in DB.")

                # Break if no more pages
                if page >= 17: # will run  pages
                    break
                page += 1
            print(f"Imported list popular series done! success")
            return JsonResponse({'message': 'Bulk import successful'}, status=200)
        
    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
        return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)