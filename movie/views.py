from django.shortcuts import render, redirect

from .models import Movie

# from django.contrib import messages


def list_movie(request):
    try:
        if Movie:
            movies = Movie.objects.all()[:5]
            return render(request, 'movie/list_movie.html', {'movies': movies})
        else:
            return f'No movies found in the database'
    except Exception as e:
        print(f" error :{e}")


def detail_movie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    movie = Movie.objects.get(id=pk)
    return render(request,'movie/detail_movie.html', {'movie': movie})


