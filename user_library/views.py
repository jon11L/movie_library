from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from.models import LikedMovie, WatchList, Like
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

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like movies.")
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

        
    if request.method == "POST":

        # user = User.objects.get(id=request.user.id)
        user = request.user
        movie = get_object_or_404(Movie, id=pk)

        # check if the movie is already liked by the user, if so remove the like.
        # if LikedMovie.objects.filter(id=request.user.id, movie=movie).exists():
        liked_movie = LikedMovie.objects.filter(user=request.user.id, movie=movie)
        

        # debugging purpose
        print(f"\n movie:\n{movie}\n\n")
        print(f"\n user:\n{user}\n\n")
        print(f"\n liked_movie:\n{liked_movie}\n\n")



        if liked_movie:
            liked_movie.delete()
            # LikedMovie.objects.remove(user=user.id)
            print("\n Unliking Movie.")
            messages.success(request, "Movie removed from your likes.")
            # return redirect(to='main:home')
            return redirect(request.META.get('HTTP_REFERER', 'main:home'))

        else:
            liked_movie = LikedMovie.objects.create(user=request.user, movie=movie)
            # liked_movie.save()
            print("\nMovie Liked")
            messages.success(request, "Movie added to your likes.")

            # return redirect(to='main:home')
            return redirect(request.META.get('HTTP_REFERER', 'main:home'))
            




def toggle_like(request, content_type: str, object_id: int):

    # Error if the user is not logged in
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like movies.")
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

    # user clicked the 'like' button
    if request.method == "POST":

        print(f"\n user_id:\n{request.user}\n\n") # debugging. check the user
        # if the Model is not recognized as in the Like model set throw message error
        valid_type = dict(Like.CONTENT_TYPE_CHOICES)
        print(f"\n valid_type:\n{valid_type}\n\n") # debugging

        if content_type not in valid_type:
            messages.error(request, "Invalid content. spell error probably")
            print(f"\n targeted model type not valid:\n\n") # debugging

            return redirect(request.META.get('HTTP_REFERER', 'main:home'))
        
        else:
            # check if the Like already exists, if so removes it
            like = Like.objects.filter(user=request.user, content_type=content_type, object_id=object_id).first()
            print(f"\n like exist?:\n{like}\n\n") # debugging 

            if like:
                like.delete()
                messages.success(request, "Movie removed from your likes.")
                print("Unlike")
                return redirect(request.META.get('HTTP_REFERER', 'main:home'))
            
            else: # the Like is created with the user id, model type and the respective id of this model
                Like.objects.create(user=request.user, content_type=content_type, object_id=object_id)
                print("Liked")
                messages.success(request, f"{content_type} added to your likes.")
                return redirect(request.META.get('HTTP_REFERER', 'main:home'))
