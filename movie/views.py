from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse



from .models import Movie
from user_library.models import Like
from .services import add_movies_from_tmdb

# from django.contrib import messages

def list_movie(request):
    '''retrieve the movies from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    try:
        if Movie:
            # movies = Movie.objects.all()[:24] # will implement a 24 content per page
            movies = Movie.objects.order_by('-id')[:24]
            
            # Get the user's like content
            user_liked_movies = []
            user_liked_movies = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='movie'
                                            ).values_list('object_id', flat=True)

            context = {
                'movies': movies,
                'user_liked_movies': user_liked_movies
                }

            return render(request, 'movie/list_movie.html', context=context)
            
        else:
            return f'No movies found in the database'
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :{e}")


def detail_movie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.
        will pass on with the necessary information such as 'Like' 
    '''
    try:
        if Movie:
        # retrieve the specified movie requested by user
            movie = Movie.objects.get(id=pk)

            # Check if user's like the movie
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
                }
            
            return render(request,'movie/detail_movie.html', context=context)
        
        else:
            return f'No movies found in the database'
        
    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")


def import_movie(request, tmdb_id):
    '''Import a movie in making a request to TMDB api and store it in the database'''
    print(f"request importing a new movie")

    if request.method == 'GET':
        result = add_movies_from_tmdb(tmdb_id)
        
        # Determine appropriate HTTP status code
        status_code = {
            'added': 201,
            'exists': 200,
            'error': 404
        }.get(result['status'], 400)
        
        return JsonResponse(result, status=status_code)


        # return JsonResponse(result, status=200 if result['status'] == 'added' else 304)