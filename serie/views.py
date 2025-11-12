from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
# from django.http import JsonResponse
from django.core.paginator import Paginator

import time

from rest_framework import generics, filters
from core.permissions import IsAdminOrIsAuthenticatedReadOnly
# from .serializer import MovieSerializer
from .serializers import SerieListSerializer, SerieDetailSerializer
from rest_framework.throttling import AnonRateThrottle

from core.throttle import AdminRateThrottle, UserBurstThrottle, UserSustainThrottle, UserDayThrottle

from .models import Serie, Season, Episode
from user_library.models import Like, WatchList
from comment.models import Comment
from comment.forms import CommentForm


class SerieListView(generics.ListCreateAPIView):
    # queryset = Movie.objects.all().order_by('-id')
    queryset = Serie.objects.select_related().prefetch_related().order_by('id')

    serializer_class = SerieListSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', "genre"]
    ordering_fields = ['first_air_date', "vote_average", "status"]
    throttle_classes = [
        AnonRateThrottle,
        AdminRateThrottle,
        UserBurstThrottle,
        UserSustainThrottle,
        UserDayThrottle,
    ]


class SerieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Serie.objects.all()
    serializer_class = SerieDetailSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    throttle_classes = [
        AnonRateThrottle,
        AdminRateThrottle,
        UserBurstThrottle,
        UserSustainThrottle,
        UserDayThrottle,
    ]


def serie_list(request):
    '''retrieve the series from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    start_time = time.time()

    try:
        if Serie:
            # paginator implementation
            if request.user.is_superuser:
                series = Serie.objects.only(
                    "id", "title", "genre", "vote_average", "vote_count", "poster_images", "slug"
                ).order_by("-id")
            else:
                series = Serie.objects.raw(
                    'SELECT id, title, genre, vote_average, vote_count, poster_images, slug FROM serie ORDER BY popularity DESC NULLS LAST'
                )

            # paginates over the model
            paginator = Paginator(series, 24)
            page = request.GET.get('page') # Get the current page number from the GET request
            serie_list = paginator.get_page(page)

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

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"time: {elapsed_time:.2f} seconds.")
            return render(request, 'serie/list_serie.html', context=context)

        else:
            # if the serie does not exist in the database
            messages.error(request, "No Tv-Show found in the database")
            return redirect('main:home')

    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")
        return redirect('main:home')


def serie_detail(request, slug):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    try:
        if Serie:
            # retrieve the specified serie requested by user
            # Get the seasons and episodes related to the serie
            serie = get_object_or_404(Serie, slug=slug)
            seasons = serie.seasons.all().prefetch_related("episodes")

            # Show the cast of season 1 as main casting of the serie to display
            main_cast = None
            for season in seasons:
                if season.season_number == 1:
                    main_cast = season.casting
                    break

            print(f"main_casting: {main_cast}")
            print(f"serie {serie.title} contains: {len(seasons)} seasons")

            # get the comments related to the movie
            comments = Comment.objects.filter(
                # user=request.user.id,
                content_type = "serie",
                object_id=serie.pk
                ).order_by('-created_at')

            print(f"number of comments: {len(comments)}")

            form = CommentForm()
            context = {
                'serie': serie,
                'seasons': seasons,
                'form': form,
                'main_cast': main_cast,
                # 'user_liked_serie': user_liked_serie,
                # 'user_watchlist_series': user_watchlist_series,
                'comments': comments
                }

            if request.user.is_authenticated:
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

                # display the Comment form if user is connected
                form = CommentForm(request.POST or None)
                context.update(
                    {
                        "serie": serie,
                        "seasons": seasons,
                        "main_cast": main_cast,
                        "user_liked_serie": user_liked_serie,
                        "user_watchlist_series": user_watchlist_series,
                        "form": form,
                        "comments": comments,
                    }
                )

            return render(request,'serie/detail_serie.html', context=context)

            # return render(request,'serie/detail_serie.html', context=context)

        # if the serie does not exist in the database
        else:
            messages.error(request, "No Tv Show found in the database with this title")
            print(f" error : Serie model not found in the database")
            return redirect('serie:list_serie')

    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}")
        return redirect('main:home')
