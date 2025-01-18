from django.shortcuts import render, redirect
from django.contrib import messages


from .models import Movie
from user_library.models import Like

# from django.contrib import messages

def list_movie(request):
    try:
        if Movie:
            # movies = Movie.objects.all()[:24] # will implement a 24 content per page
            movies = Movie.objects.order_by('-id')[:8]
            
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
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")


def detail_movie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.
        will pass on with the necessary information such as 'Like' 
    '''
    try:
        if Movie:
        # retrieve the specified movie requested by user
            movie = Movie.objects.get(id=pk)

        if request.user.is_authenticated:

                # Check if user's like the movie
                user_liked_movies = False
                user_liked_movies = Like.objects.filter(
                                                user=request.user.id,
                                                content_type='movie',
                                                object_id=movie.pk
                                                )

                print(f"user_liked :{user_liked_movies}") # debug print

                context = {
                    'movie': movie,
                    'user_liked_movies': user_liked_movies
                    }

                return render(request,'movie/detail_movie.html', context=context)

    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")

