from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
# from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Serie, Season, Episode
from user_library.models import Like, WatchList
from comment.models import Comment
from comment.forms import CommentForm


def list_serie(request):
    '''retrieve the series from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    try:
        if Serie:
            # paginator implementation
            # p = Paginator(Serie.objects.all().order_by('-popularity'), 24)
            p = Paginator(Serie.objects.all().order_by('-id'), 24)
            # Get the current page number from the GET request
            page = request.GET.get('page') 
            serie_list = p.get_page(page)

            # Get the user's watchlist content (series only here)
            user_watchlist_series = WatchList.objects.filter(
                                                user=request.user.id,
                                                serie__isnull=False
                                                ).values_list('serie_id', flat=True)

            # Get the user's like content
            user_liked_series = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='serie'
                                            ).values_list('object_id', flat=True)

            context = {
                'user_liked_series': user_liked_series,
                'user_watchlist_series': user_watchlist_series,
                'serie_list' : serie_list,
            }

            return render(request, 'serie/list_serie.html', context=context)
        
        else:
            # if the serie does not exist in the database
            messages.error(request, "No Tv-Show found in the database")
            return redirect('main:home')
        
    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")
        return redirect('main:home')


def serie_overview(request, slug):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    try:
        if Serie:
        # retrieve the specified serie requested by user
            serie = get_object_or_404(Serie, slug=slug)
            # Get the seasons and episodes
            seasons = serie.seasons.all().prefetch_related("episodes")
            print(f"serie {serie.title} contains: {len(seasons)} seasons")

            # Get the user's watchlist content (movies, series)
            user_watchlist_series = WatchList.objects.filter(
                                                user=request.user.id,
                                                serie__isnull=False
                                                ).values_list('serie_id', flat=True)

            # Check if user liked the serie
            user_liked_serie = Like.objects.filter(
                                            user=request.user.id,
                                            content_type='serie',
                                            object_id=serie.pk
                                            ).values_list('object_id', flat=True)

            print(f"user like {serie.title} :{user_liked_serie}") # debug print

            # get the comments related to the movie
            comments = Comment.objects.filter(
                # user=request.user.id,
                content_type = "serie",
                object_id=serie.pk
                ).order_by('-created_at')
            
            print(f"number of comments: {len(comments)}")

            # display the Comment form if user is connected
            if request.user.is_authenticated:
                form = CommentForm(request.POST or None)

                context = {
                    'serie': serie,
                    'seasons': seasons,
                    'user_liked_serie': user_liked_serie,
                    'user_watchlist_series': user_watchlist_series,
                    'form': form,
                    'comments': comments,
                    }

                return render(request,'serie/detail_serie.html', context=context)

            else:
                form = CommentForm()
                context = {
                    'serie': serie,
                    'seasons': seasons,
                    'form': form,
                    'user_liked_serie': user_liked_serie,
                    'user_watchlist_series': user_watchlist_series,
                    'comments': comments
                    }
                return render(request,'serie/detail_serie.html', context=context)
            
        # if the serie does not exist in the database
        else:
            messages.error(request, "No Tv Show found in the database with this title")
            print(f" error : Serie model not found in the database")
            return redirect('serie:list_serie')
        
    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
        return redirect('main:home')
