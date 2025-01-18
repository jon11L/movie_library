from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from.models import WatchList, Like
from user.models import User
from movie.models import Movie


def user_liked_content_view(request):
    '''retrieve the user's liked mvoie list from the database and display them in the template'''

    if request.user.is_authenticated:
        if request.method == "GET":

        # fetch the profile being requested
            user = User.objects.get(id=request.user.id)
            liked_content = Like.objects.filter(user=request.user)
            # movies = [content.movie for content in liked_content]

            context = {
                'liked_content': liked_content,
                # 'movies': movies,
                'user': user
            }

            return render(request, 'user_library/liked_content.html', context=context)



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
        


def toggle_like(request, content_type: str, object_id: int):

    # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like contents.")
        return redirect(request.META.get('HTTP_REFERER', 'main:home'))

    # user clicked the 'like' button
    if request.method == "POST":

        # if the Model is not recognized as in the Like model set throw message error
        valid_type = dict(Like.CONTENT_TYPE_CHOICES)

        if content_type not in valid_type:
            messages.error(request, "Invalid content. spelling error probably")
            print(f"\n targeted model type not valid:\n") # debugging

            return redirect(request.META.get('HTTP_REFERER', 'main:home'))
        
        else:
            # check if the Like already exists, if so removes it
            like = Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=object_id
                ).first()
            
            print(f"\n like exist?: {like}\n") # debugging 

            if like: # If the like already exists, it will be removed.
                like.delete()
                messages.success(request, "Content removed from your likes.")
                print("Unlike")
                return redirect(request.META.get('HTTP_REFERER', 'main:home'))
            
            else: # the Like is created with the user id, model type and the respective id of this model
                Like.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id
                    )
                
                print("**Liked**\n")
                messages.success(request, f"{content_type} added to your likes.")
                return redirect(request.META.get('HTTP_REFERER', 'main:home'))
