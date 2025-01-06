from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import User, Profile

# Create your views here.
def login_user(request):
    try:

        if request.method == "GET":
            return render(request, 'user/login.html', {})

            # TODO
            # TODO check if user credentials match existing user
            # TODO if not, render the login page
            # TODO if yes, redirect to user's profile page
            # TODO if user has admin rights, redirect to admin dashboard

        elif request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect(to='/')
            else:

                print("User not found")
                messages.error(request, ("User and password don't match. Please try again"))
                return render(request, 'user/login.html', {})
    
    except Exception as e:
        return f"An error occurred:\n\n {e}"

def logout_user(request):
    logout(request)
    return redirect(to='/')


def profile_page(request, pk):
    # TODO if user is authenticated, render user's profile page
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user=request.user)
        # current_user_rofile = 
    
        context = {
            'user': current_user,
            # 'current_user_rofile': current_user_rofile,
            # 'user_id': pk
        }
        return render(request, 'user/profile_page.html', context=context)
    
    else:
        messages.success(request, ("You must be logged in to access this Page"))
        return redirect(to='/login')