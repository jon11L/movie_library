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
                                f"Account successfully created!\n Hello, {username}! You are now logged in."
                                f"\nClick here to complete your profile"
                                )
                return redirect(to='/')
            except Exception as e:
                print(f"An error occurred:\n\n {e}")
                return HttpResponse("An error occurred while trying to register the user.  Please try again")
            
        else:
            
            return render(request, 'user/register.html', {'form': form, 'error': 'Form is not valid'})





# Create your views here.
def login_user(request):
    try:

        if request.method == "GET": # user request to go to the login page url
            return render(request, 'user/login.html', {})

        elif request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, ("You are now logged in!"))
                return redirect(to='/')
            else:

                print("User not found")
                messages.error(request, ("User and password don't match. Please try again"))
                return redirect('login')
    
    except Exception as e:
        print(f"An error occurred:\n\n {e}")
        return HttpResponse("An error occurred while trying to authenticate the user.  Please try again")


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out!"))
    return redirect(to='/')



@login_required
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
        return redirect(to='/login')
    



def edit_profile(request, pk):
    ''' User can submit form to edit profile'''
    if request.user.is_authenticated:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
        if request.method == 'GET':
            form = EditProfileForm()
            return render(request, 'user/edit_profile.html', {'form': form})

    if request.method == 'POST':
        # update the profile with the new information
        form = EditProfileForm(request.POST)
        if form.is_valid():
            form.save()

            # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
    
        context = {
            'profile': profile,
            # 'current_user_rofile': current_user_rofile,
            # 'user_id': pk
        }
            
        return redirect(to=f'/user/profile_page.html')

        
    #     if form.is_valid():
    #         user = User.objects.get(pk=pk)

            
    pass

