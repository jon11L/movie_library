from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

import time

from core.tools.wrappers import timer, num_queries


from .models import Profile
from .forms import RegisterForm, EditProfileForm, UpdateUserForm
from user_library.models import Like, WatchList
from comment.models import Comment
from movie.models import Movie
from serie.models import Serie


def register_user(request):
    '''User registration page'''
    if request.method == 'GET':
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect(to='main:home')

        form = RegisterForm()  # Create an instance of the form
        return render(request, 'user/register.html', {'form': form})  # Render the form to the user.

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # might not need to retrieve the username & pw

            try:
                login(request, user)
                messages.success(request,
                                f"Account successfully created!    Hello, {username}! You are now logged in."
                                f"Click here to complete your profile"
                                )

                return redirect(to='main:home')
            
            except Exception as e:
                print(f"An error occurred:\n\n {e}")
                # raise HttpResponse("An error occurred while trying to register the user.\nPlease refresh the page and try again")
                return redirect(to='user:register')

        else:
            messages.error(request, "It seems some fields entered was not valid, Please check and try again")
            return render(request, 'user/register.html', {'form': form, 'error': 'Form is not valid'})


def login_user(request):
    '''User login view page'''

    if request.method == "GET": # user request to go to the login page url
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect(to='main:home')
        
        return render(request, 'user/login.html', {})

    elif request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                print(f"\n- User '{user.username}' logged in. \n")
                messages.success(request, (f"logged in! Hello {user.username}."))
                return redirect(to='main:home')

            else:
                print("\n - User not found OR credentials don't match. \n")
                messages.error(request, ("User and password don't match. Please try again"))
                return redirect(to='user:login')
            
        except Exception as e:
            print(f"An error occurred:\n\n {e}")
            # raise HttpResponse("An error occurred while trying to log in the user.\nPlease refresh the page and try again")
            return redirect(to='user:login')


# log out function
@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out!"))
    return redirect(to='/')


@timer
@num_queries
@login_required(login_url= "user:login")
def profile_page(request, pk):
    ''' Returns the profile page of the user_id/pk requested
        At the moment users can visit other user's profile, but this may be changed
    '''
    if request.user.is_authenticated:
        # fetch the profile being requested
        # retrieve the user and its related Profile in one query
        user = User.objects.filter(pk=pk).select_related("profile").first()

        print(f"\nUser query: {user}\n") # debug print

        like = Like.objects.filter(user=pk)

        # Displaying the comment posted by the user
        comments = Comment.objects.filter(user=pk).select_related("movie", "serie")[0:3]

        # load the last 3 Watchlist added by the user
        watchlist_items = WatchList.objects.filter(user=pk).select_related("movie", "serie")[0:3]
        
        print(f"\nwatchlist_items: {watchlist_items}\n\n") # debug print

        # get the content (movie/serie) related to each comment.
        #  Only poster_image, title and genre needed
        last_watchlist = []
        for item in watchlist_items:
            if item.content_object:
                last_watchlist.append({
                    # 'object': item.content_object, # retrieve the whole object through foreign key
                    'kind': item.kind,
                    'added_on': item.created_at.strftime("%d %B %Y"),
                    'poster': item.content_object.render_poster(),
                    'title': item.content_object.title,
                    'genre': item.content_object.render_genre(),
                    'slug': item.content_object.slug,
                })
        # print(f"\nlast_watchlist: {last_watchlist}\n") # debug print

        # Templates for future fav movies display
        # fav_movies = (1, 2, 3)

        # fetch the movies and series that are commented by the user
        comment_list = []
        for comment in comments:

            if comment.content_object:
                comment_list.append({
                    # 'object': comment.content_object,
                    'id': comment.pk,
                    'body': comment.body,
                    # 'user': comment.user.username,  Removed many queries
                    'created_at': comment.created_at.strftime("%d %B %Y"),
                    'kind': comment.kind,
                    'title': comment.content_object.title,
                    'poster': comment.content_object.render_poster(),
                    'slug': comment.content_object.slug,
                })

        print(f"comment_list: {comment_list[0:3]}\n") # debug print

        profile_card = {
            'user_id': user.profile.user,
            'age': user.profile.render_age(),
            'name': user.profile.user.username.capitalize(),
            'bio': user.profile.bio,
            'profile_picture': user.profile.profile_picture.url if user.profile.profile_picture else None,
            'background_picture': user.profile.render_background_picture(),
            'watchlist_status': user.profile.watchlist_private,
            'last_update': user.profile.last_update()
        }

        context = {
            'user_id': user.pk,
            'profile_card':profile_card,
            'likes': like.count(),
            'comments': comment_list,
            'last_watchlist': last_watchlist,
            # 'fav_movies': fav_movies
        }

        return render(request, 'user/profile_page.html', context=context)
    
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')


def update_profile(request, pk):
    ''' User can submit form to edit profile.
        Only the user himself can access this page.
        If someone tries to access another user's profile update page, they will be redirected to their own profile.
        request.user.id must be same as the target profile.user_id OR user.id/pk. 
    '''
    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User_Profile_update_page *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
        if request.method == 'GET':
            form = EditProfileForm(instance=profile)

            return render(request, 'user/edit_profile.html', {'form': form})

        if request.method == 'POST':
            # update the profile with the new information
            form = EditProfileForm(request.POST or None, request.FILES or None, instance=profile)

            if form.is_valid():
                form.save()

                print(f"\n - User '{profile.user.username}' updated their Profile. \n")
                messages.success(request, "Profile updated!")
                return redirect(to=f'user:profile_page', pk=pk) 
            
            else:
                messages.error(request, "Please correct the errors in the form.")
                return render(request, 'user/edit_profile.html', {'form': form})
        
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')


def update_user(request, pk):
    ''' User can submit form to edit their first_name, last_name and user_name'''

    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User_update_page *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        # fetch the profile being requested
        current_user = User.objects.get(pk=pk)

        if request.method == 'GET':
            form = UpdateUserForm(instance=current_user)

            return render(request, 'user/edit_user.html', {'form': form})

        if request.method == 'POST':
            # update the profile with the new information
            form = UpdateUserForm(request.POST, instance=current_user)

            if form.is_valid():
                current_user = form.save()

                print("User's credentials were updated.")
                messages.success(request, "your credential was updated!")
                return redirect(to=f'user:profile_page', pk=pk) 
            else:
                messages.error(request, "Please correct the errors in the form.")
                return render(request, 'user/edit_user.html', {'form': form})
        
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')


def update_password(request, pk):
    ''' User can request to change their password'''

    if request.user.is_authenticated and request.user.id != pk:
        print("\n* Unauthorised acces: user tried to access another User's account setting *\n")
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)

    elif request.user.is_authenticated and request.user.id == pk:
        # fetch the profile being requested
        user = User.objects.get(pk=pk)

        if request.method == 'GET':
            form = PasswordChangeForm(user=user)
            return render(request, 'user/edit_password.html', {'form': form})

        if request.method == 'POST':
            # update the profile with the new information
            form = PasswordChangeForm(user=request.user, data=request.POST)

            if form.is_valid():
                user = form.save() # save the new forms data and return the updated User

                update_session_auth_hash(request, user) # refresh the session with the new password

                messages.success(request, "your password was updated!")
                return redirect(to=f'user:profile_page', pk=pk) 
            else:
                print("Something went wrong, password not matching or too short")
                messages.error(request, "Something went wrong, password not matching or too short.\nTry again.")
                return render(request, 'user/edit_password.html', {'form': form})
        
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')


#  Will be implemented in a separate models for account settings/preferences of user
def toggle_watchlist_privacy(request):
    '''
    This function is called when the user clicks on the button to toggle the watchlist status
    between private and public.
    It is called via HTMX and updates the database without reloading the page.
    '''

    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'Login required',
            'message': "You must be logged-in to change your watchlist status."
            }, status=401)
    
    if request.method == "POST":

        # check if the privacy status of the user is set to True or False and change accordingly
        profile = Profile.objects.get(user=request.user)
        if profile.watchlist_private == True:
            profile.watchlist_private = False
        else:
            profile.watchlist_private = True
        profile.save()# update the profile watchlist status

        status = "Private" if profile.watchlist_private else "Public"
        # message = f"Your watchlist is now {status}."
        print(f"User {request.user}'s Watchlist status changed to: {status}\n")

        # return JsonResponse({'new_status': status, 'message': message})
        context = {
            'profile': profile,
        }
        # messages.success(request, f"Your watchlist is now {status}.") # need to pass the message directly on HTMX to avoid reloading & duplication
        return render(request, 'user/partials/toggle_privacy_watchlist.html', context=context)