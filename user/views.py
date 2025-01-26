from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import Profile
from .forms import RegisterForm, EditProfileForm, UpdateUserForm
from user_library.models import Like


def register_user(request):
    '''User registration page'''
    if request.method == 'GET':
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
                raise HttpResponse("An error occurred while trying to register the user.\nPlease refresh the page and try again")
            
        else:
            messages.error(request, "It seems some fields entered was not valid, Please check and try again")
            return render(request, 'user/register.html', {'form': form, 'error': 'Form is not valid'})


def login_user(request):
    '''User login view page'''

    if request.method == "GET": # user request to go to the login page url
        return render(request, 'user/login.html', {})

    elif request.method == "POST":
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


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out!"))
    return redirect(to='/')


def profile_page(request, pk):
    ''' Returns the profile page of the user_id/pk requested
        At the moment users can visit other user's profile, but this may be changed
    '''
    if request.user.is_authenticated:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
        like = Like.objects.filter(user=pk)
        # print(f"like: {like}") # debug print

        total_like = like.count() #count how many items has been liked

        context = {
            'profile': profile,
            'like': like,
            'total_like': total_like,
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
            return render(request, 'user/edit_pw.html', {'form': form})

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
                return render(request, 'user/edit_pw.html', {'form': form})
        
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')
