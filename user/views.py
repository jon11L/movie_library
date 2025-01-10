from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse


from .models import Profile
from .forms import RegisterForm, EditProfileForm


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

            try:
                login(request, user)

                messages.success(request,
                                f"Account successfully created!    Hello, {username}! You are now logged in."
                                f"    Click here to complete your profile"
                                )
                return redirect(to='main:home')
            except Exception as e:
                print(f"An error occurred:\n\n {e}")
                raise HttpResponse("An error occurred while trying to register the user.  Please try again")
            
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
            messages.success(request, (f"logged in! Hello {user.username}."))
            return redirect(to='main:home')
        else:

            print("User not found")
            messages.error(request, ("User and password don't match. Please try again"))
            return redirect(to='user:login')



@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out!"))
    return redirect(to='/')



def profile_page(request, pk):

    if request.user.is_authenticated:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
    
        context = {
            'profile': profile,

        }
        return render(request, 'user/profile_page.html', context=context)
    # need to add a check if a user visit another user's profile. To allow it or not?
    
    else:
        messages.success(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')
    


def update_profile(request, pk):
    ''' User can submit form to edit profile'''

    if request.user.id != pk:
        messages.error(request, ("You are not authorized to acces this page."))
        return redirect(to='user:profile_page', pk=request.user.id)
        
    if request.user.is_authenticated:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
        if request.method == 'GET':
            form = EditProfileForm()

            return render(request, 'user/edit_profile.html', {})

        if request.method == 'POST':
            # update the profile with the new information
            form = EditProfileForm(request.POST or None, instance=profile)
            if form.is_valid():
                form.save()

                # fetch the profile being requested
            profile = Profile.objects.get(user_id=pk)

            # context = {
            #     'profile': profile,
            # }

            return redirect(to=f'user:profile_page') 
        
    else:
        messages.error(request, ("You must be logged in to access this page"))
        return redirect(to='user:login')
