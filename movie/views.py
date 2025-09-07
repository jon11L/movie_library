from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from rest_framework import viewsets
from rest_framework import generics

from .permissions import IsAdminOrIsAuthenticatedReadOnly
# from .serializer import MovieSerializer
from .serializer import MovieListSerializer, MovieDetailSerializer



from .models import Movie
from user_library.models import Like, WatchList
from comment.models import Comment
from comment.forms import CommentForm



# def admin_check(user):
#     return user.is_superuser  # or user.is_staff for staff users


# class MovieViewSet(viewsets.ModelViewSet):
#     '''View to serialize Movie model'''
#     # authentication_classes = [SessionAuthentication, BasicAuthentication]
#     queryset = Movie.objects.all().order_by('-id')
#     serializer_class = MovieSerializer
#     permission_classes = [IsAdminOrIsAuthenticatedReadOnly]


# API views
class MovieListView(generics.ListCreateAPIView):
    queryset = Movie.objects.all().order_by('-id')
    serializer_class = MovieListSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]


class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]


# Regular template views
def movie_list(request):
    '''retrieve the movies from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    user_liked_movies = []
    user_watchlist_movies = []

    try:
        if Movie:
            # paginator implementation
            if request.user.is_superuser:
                paginator = Paginator(Movie.objects.all().order_by('-id'), 24)
            else:
                paginator = Paginator(Movie.objects.all().order_by('-popularity'), 24)
                
            # Get the current page number from the GET request
            page = request.GET.get('page')
            movie_list = paginator.get_page(page)

            # Get the user's watchlist content (movies, series)
            user_watchlist_movies = set(
                WatchList.objects.filter(
                    user=request.user.id, 
                    movie__isnull=False
                    ).values_list('movie_id', flat=True)
            )

            # Get the user's like content
            user_liked_movies = set(
                Like.objects.filter(
                    user=request.user.id,
                    content_type='movie'
                    ).values_list('object_id', flat=True)
            )

            context = {
                'movie_list' : movie_list,
                'user_liked_movies': user_liked_movies,
                'user_watchlist_movies': user_watchlist_movies, 
                }

            return render(request, 'movie/list_movie.html', context=context)
            
        else:
            messages.error(request, 'No movies found in the database')
            return redirect('main:home')
        
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")
        return redirect('main:home')


def movie_detail(request, slug):
    ''' get the movie object from the database using the movie_id parameter in the URL request.\n
        will also pass on with the necessary information such as 'Like' or 'WatchList' 
    '''
    try:
        if Movie:
        # retrieve the specified movie requested by user
            movie = get_object_or_404(Movie, slug=slug)

            # Get the user's watchlist content (movies, series)
            user_watchlist_movies = set(
                WatchList.objects.filter(
                    user=request.user.id,
                    movie__isnull=False
                    ).values_list('movie_id', flat=True)
            )

            # Check if user liked the movie
            user_liked_movie = set(
                Like.objects.filter(
                    user=request.user.id,
                    content_type='movie',
                    object_id=movie.pk
                    ).values_list('object_id', flat=True)
            )

            print(f"user_liked :{user_liked_movie}") # debug print

            # get the comments related to the movie
            comments = Comment.objects.filter(
                content_type = "movie",
                object_id=movie.pk
                ).order_by('-created_at')
            
            print(f"Number of comments:\n {len(comments)}")

            # display the Comment form if user is connected
            if request.user.is_authenticated:
                form = CommentForm(request.POST or None)

                context = {
                    'movie': movie,
                    'user_liked_movie': user_liked_movie,
                    'user_watchlist_movies': user_watchlist_movies,
                    'form': form,
                    'comments': comments
                    }
                return render(request,'movie/detail_movie.html', context=context)
            
            else:
                form = CommentForm()
                context = {
                    'movie': movie,
                    'form': form,
                    'user_liked_movie': user_liked_movie,
                    'user_watchlist_movies': user_watchlist_movies,
                    'comments': comments
                    }
                return render(request,'movie/detail_movie.html', context=context)
        
        else:
            messages.error(request, "No Movie found in the database with this title")
            print(f"Movie model not found in the database")
            return redirect('movie:list_movie')
        
    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
        return redirect('main:home')
