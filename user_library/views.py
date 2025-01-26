from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from.models import WatchList, Like
from user.models import User
from movie.models import Movie
from serie.models import Serie


def user_liked_content_view(request, pk):
    '''retrieve the user's liked mvoie list from the database and display them in the template'''

    if request.user.is_authenticated:
        if request.method == "GET":

            # movies= []
            # series= []
            # fetch the profile being requested
            user = User.objects.get(id=pk)
            print(f" user: {user}\n")


            likes = Like.objects.filter(user=request.user)
            print(f" liked_content: {likes}\n") #debug print


            liked_content = []
            for like in likes:
                if like.content_type == "movie":
                    try:
                        movie = Movie.objects.get(id=like.object_id)
                        liked_content.append(movie)
                        print(f"movie: {movie}\n") #debug print
                    except Movie.DoesNotExist:
                        continue
                elif like.content_type == "serie":
                    try:
                        serie = Serie.objects.get(id=like.object_id)
                        liked_content.append(serie)
                        print(f"serie: {serie}\n") #debug print
                    except Serie.DoesNotExist:
                        continue


            total_like = likes.count() #count how many items has been liked


            context = {
                'likes': likes,
                'liked_content': liked_content,
                # 'movies': movies,
                'total_like': total_like,
                'user': user
            }

            return render(request, 'user_library/liked_content.html', context=context)
        
        else:
            return redirect('user:login')



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
    '''When triggered or called, this functin will check in the Like models data
    if an instance of this like between user/content_type/id exist or not 
    if it does not, it will then create a new instance in the database,
    if the instance already exists, it will delete the instance.
    '''

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
