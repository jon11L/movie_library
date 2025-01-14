from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from.models import LikedMovie, WatchList
from user.models import User #, Profile
from movie.models import Movie



def liked_movies_view(request, pk):
    '''retrieve the user's liked mvoie list from the database and display them in the template'''

    if request.user.is_authenticated:
        if request.method == "GET":

        # fetch the profile being requested
            user = User.objects.get(id=pk)
            liked_movies = LikedMovie.objects.filter(user=pk)
            movies = [liked_movie.movie for liked_movie in liked_movies]

            context = {
                'movies': movies,
                'user': user
            }

            return render(request, 'user_library/liked_movies.html', context=context)
    


        # elif request.method == "POST":
        #     # add a movie to the user's liked movie list
        #         movie_id = request.POST['movie_id']
        #         user_id = request.POST['user_id']

        #         # check if the movie is already in the liked movies list
        #         if LikedMovie.objects.filter(user=pk, movie=movie_id).exists():
        #             print("Movie already in liked movies list")

        #         else:
        #             liked_movie = LikedMovie(user=user, movie=Movie.objects.get(id=movie_id))
        #             liked_movie.save()
        



def watch_list(request, pk):
    '''retrieve the user's watchlist from the database and display them in the template'''

    if request.method == "GET":

        if request.user.is_authenticated:
        # fetch the profile being requested
            user = User.objects.get(id=pk)
            watchlist_movies = WatchList.objects.filter(user=pk)
            movies = [watchlist_movie.movie for watchlist_movie in watchlist_movies]

            context = {
                'movies': movies,
                'user': user
            }

            return render(request, 'user_library/watch_list.html', context=context)
        



def add_to_liked_movie(request, pk):
    '''add a movie to the user's liked movie list'''
        
    if request.user.is_authenticated and request.method == "GET":

        user = User.objects.get(id=request.user.id)
        movie = get_object_or_404(Movie, id=pk)

        # check if the movie is already liked by the user, if so remove the like.
        # if LikedMovie.objects.filter(id=request.user.id, movie=movie).exists():
        liked_movie =  LikedMovie.objects.filter(user=request.user.id, movie=movie).first()
        if liked_movie:
            liked_movie.delete()
            # LikedMovie.objects.remove(user=user.id)
            print("Movie already in liked movies list")
            messages.success(request, "Movie removed from your likes.")
            return redirect(to='main:home')

        else:
            liked_movie = LikedMovie.objects.get_or_create(user=request.user, movie=movie)
            # liked_movie.save()
            messages.success(request, "Movie added to your likes.")

            return redirect(to='main:home')