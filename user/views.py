from django.shortcuts import render

# from django.contrib.auth import authenticate, login, logout


# Create your views here.
def login(request):

    if request.method == "GET":
        return render(request, 'user/login.html', {})
