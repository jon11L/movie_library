from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import User, Profile

# Create your views here.
def login_user(request):
    try:

        if request.method == "GET":
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



def logout_user(request):
    logout(request)
    messages.success(request, ("You are now logged out!"))
    return redirect(to='/')



@login_required
def profile_page(request, pk):

    if request.user.is_authenticated:
        # fetch the profile being requested
        profile = Profile.objects.get(user_id=pk)
    
        context = {
            'user': profile,
            # 'current_user_rofile': current_user_rofile,
            # 'user_id': pk
        }
        return render(request, 'user/profile_page.html', context=context)
    
    else:
        messages.success(request, ("You must be logged in to access this Page"))
        return redirect(to='/login')