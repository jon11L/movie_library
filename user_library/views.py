from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from.models import WatchList, Like
from user.models import User
from movie.models import Movie
from serie.models import Serie


def liked_content_view(request, pk):
    '''retrieve the user's liked contents from the database 
    and display them in the template. 
    '''
    # Need to add a check that only current user can visit their own Like page.
    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User_update_page *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        if request.method == "GET":

            user = User.objects.get(id=pk)
            print(f" user: {user}\n")

            likes = Like.objects.filter(user=pk)
            # print(f" liked_content: {likes}\n") #debug print

            liked_content = [] # intialize the list of liked content 
            for like in likes:
                if like.content_type == "movie":
                    try:
                        movie = Movie.objects.get(id=like.object_id)
                        liked_content.append({'content_type': like.content_type, 'content': movie, 'liked_on': like.liked_on.strftime("%d %B %Y")})
                        # print(f"movie: {movie}\n") #debug print
                    except Movie.DoesNotExist:
                        continue

                elif like.content_type == "serie":
                    try:
                        serie = Serie.objects.get(id=like.object_id)
                        liked_content.append({'content_type': like.content_type, 'content': serie, 'liked_at': like.liked_on.strftime("%d %B %Y")})
                        # print(f"serie: {serie}\n") #debug print
                    except Serie.DoesNotExist:
                        continue

            total_like = likes.count() #count how many items has been liked

            # print(f"all liked content: {liked_content}")

            context = {
                'liked_content': liked_content,
                'total_like': total_like,
            }

            return render(request, 'user_library/liked_content.html', context=context)


            # user clicked the 'like' button
        elif request.method == "POST":
            # user clicked the 'unlike' button
            if request.POST.get('like_button_clicked') == 'true':
                print(f"like button clicked\n") # debugging
            pass

    else:
        messages.error(request, "You must be logged in to view your liked content.")
        return redirect('user:login')



def toggle_like(request, content_type: str, object_id: int):
    '''When triggered or called in pair with AJAX on the front-end, 
    this function will check in the 'Like' models data
    if an instance of Like exist between user/content_type (movie or serie)/object_id (id of that object) exist or not 
    if it does not, it will then create a new instance in the database,
    if the instance already exists, it will delete the instance.
    With AJAX implemented on the front-end, the updates on the data are made without reloading the page
    '''

    # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        # messages.error(request, "You must be logged in to like contents.")
        return JsonResponse({
            'error': 'Login required',
            'message': "You must be logged in to like contents."
            }, status=401)

    # User clicked the 'like' button.
    if request.method == "POST":

        # if the Model is not recognized as in the <Like model> set throw message error
        valid_type = dict(Like.CONTENT_TYPE_CHOICES)

        if content_type not in valid_type:
            # messages.error(request, "Invalid content.")
            print(f"\n targeted model type not valid:\n") # debugging

            return JsonResponse({
                'error': 'Invalid content type',
                'message': "Invalid content."
                }, status=400)
        
        else:
            # check if the Like already exists
            like = Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=object_id
                ).first()
            print(f"\n like exist?: {like}\n") # debugging 

            if like: # If the like already exists, it will be removed.
                like.delete()
                print(f"'{like}' Unliked")
                message = f"{content_type} removed from your likes."
                return JsonResponse({'liked': False, 'message': message}) # responding to Ajax on front-end.
            
            else: # the Like is created with the user id, model type and the respective id of this model
                like = Like.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id
                    )
                
                print(f"**Liked**.\n{like}\n")
                # messages.success(request, f"{content_type} added to your likes.")
                message = f"{content_type} added to your likes."
                return JsonResponse({'liked': True, 'message': message}) # responding to Ajax on front-end.





def watch_list_view(request, pk):
    '''retrieve the user's watchlist from the database and display them in the template'''

    # Need to add a check that only current user can visit their own Like page.
    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User_watchlist *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        if request.method == "GET":

            # fetch the profile being requested
            user = User.objects.get(id=pk)
            watchlist = WatchList.objects.filter(user=pk)

            watchlist_content = [] # intialize the list of watchlist instances 
            for item in watchlist:
                if item.content_type == "movie":
                    try:
                        movie = Movie.objects.get(id=item.object_id)
                        watchlist_content.append({'content_type': item.content_type, 'content': movie, 'added_on': item.created_on.strftime("%d %B %Y")})
                        # print(f"movie: {movie}\n") #debug print
                    except Movie.DoesNotExist:
                        continue

                elif item.content_type == "serie":
                    try:
                        serie = Serie.objects.get(id=item.object_id)
                        watchlist_content.append({'content_type': item.content_type, 'content': serie, 'added_on': item.created_on.strftime("%d %B %Y")})
                        # print(f"serie: {serie}\n") #debug print
                    except Serie.DoesNotExist:
                        continue

            total_content = watchlist.count()

            context = {
                'user': user,
                'watch_list_content': watchlist_content,
                'total_content': total_content,
            }

            return render(request, 'user_library/watch_list.html', context=context)

        elif request.method == "POST":
            # user clicked the 'unlike' button
            if request.POST.get('watchlist_button_clicked') == 'true':
                print(f"watchlist button clicked\n") # debugging
            pass

    else:
        messages.error(request, "You must be logged in to view your liked content.")
        return redirect('user:login')




def toggle_watchlist(request, content_type: str, object_id: int):
    '''When triggered or called in pair with AJAX on the front-end, 
    this function will check in the 'watchlist' models data
    if an instance of watchlist exist between user/content_type (movie or serie)/object_id (id of that object) exist or not 
    if it does not, it will then create a new instance in the database,
    if the instance already exists, it will delete the instance.
    With AJAX implemented on the front-end, the updates on the data are made without reloading the page
    '''

    # if user is Not logged in, it a message will pop up
    if not request.user.is_authenticated:
        # messages.error(request, "You must be logged in to like contents.")
        return JsonResponse({
            'error': 'Login required',
            'message': "You must be logged to use the Watchlist feature."
            }, status=401)

    # user clicked the 'like' button
    if request.method == "POST":

        # if the Model is not recognized as in the <Like model> set throw message error
        valid_type = dict(WatchList.CONTENT_TYPE_CHOICES)

        if content_type not in valid_type:
            # messages.error(request, "Invalid content.")
            print(f"\n targeted model type not valid:\n") # debugging

            return JsonResponse({
                'error': 'Invalid content type',
                'message': "Invalid content."
                }, status=400)
        
        else:
            # check if the Like already exists
            watchlist = WatchList.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=object_id
                ).first()
            print(f"\n content exist in watchlist?: {watchlist}\n") # debugging 

            if watchlist: # If the like already exists, it will be removed.
                watchlist.delete()
                print(f"'{watchlist}' removed from watchlist")
                message = f"{content_type} removed from your watchlist."
                # return JsonResponse({'liked': False, 'message': message}) # responding to Ajax on front-end.
                return JsonResponse({'in_watchlist': False, 'message': message}) # responding to Ajax on front-end.
            
            else: # the Like is created with the user id, model type and the respective id of this model
                watchlist = WatchList.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id
                    )
                
                print(f"**ADDED** to watchlist.\n{watchlist}\n")
                # messages.success(request, f"{content_type} added to your likes.")
                message = f"{content_type} added to your watchlist."
                return JsonResponse({'in_watchlist': True, 'message': message}) # responding to Ajax on front-end.
