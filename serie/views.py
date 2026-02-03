from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
# from django.http import JsonResponse
from django.core.paginator import Paginator

from rest_framework import generics, filters
from rest_framework.throttling import AnonRateThrottle

from .serializers import SerieListSerializer, SerieDetailSerializer
from core.permissions import IsAdminOrIsAuthenticatedReadOnly
from core.throttle import AdminRateThrottle, UserBurstThrottle, UserSustainThrottle, UserDayThrottle
from core.tools.paginator import page_window # Temporary placement for paginator design
from core.tools.wrappers import timer, num_queries

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


@timer
@num_queries
def serie_list(request):
    '''retrieve the series from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    list_media = [] # list to hold the content (movies, series)
    user_liked_series = None
    user_watchlist_series = None
    sort_by = None
    base_url = "/serie/list/"
    try:
        if Serie:

            # ========== Building a sort-by feature ==========================
            sort_by = (
                # ('display name', 'django field')
                ('newest first', '-first_air_date'), 
                ('oldest first', 'first_air_date'),
                ('least popular', 'popularity'),
                ('most popular', '-popularity'),
                ('lowest vote', 'vote_count'),
                ('highest vote', '-vote_count'),
                ('A-z title', 'title'), 
                ('Z-a title', '-title'),
                ('first added', 'id'),
                ('last added', '-id'),
            )

            query_params = request.GET.copy()
            print(f"-- Query params: {query_params}\n")  # Debug print
            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')
            query_pagin_url = query_params.urlencode()

            # Allow to keep the query parameter in the url for pagination
            # query_string_url = query_params.urlencode()

            # ========== END /// Building a sort-by feature ==========================

            sel_order = '-id' # default selection order / first reach of the list page
            if 'order_by' in query_params:
                sel_order = query_params.get('order_by')
                print(f"selected order: {sel_order}")
            query_sort_url = query_params.urlencode()

            # print(query_string_url, "\n")

            series = (
                Serie.objects.only(
                    "id",
                    "title",
                    "genre",
                    "first_air_date",
                    "vote_average",
                    "vote_count",
                    "popularity",
                    "poster_images",
                    "slug",
                )
                .exclude(is_active=False)
                .exclude(first_air_date__isnull=True)
                .order_by(sel_order)
            )

            # paginates over the pre loaded query
            paginator = Paginator(series, 24)
            page = request.GET.get('page') # Get the current page number from the GET request
            page_obj = paginator.get_page(page)

            # create a standardized data stack to pass in templates.
            # Avoiding any extra hidden queries on the frontend
            for item in page_obj:
                list_media.append({
                    "id": item.pk, 
                    "title": item.title, 
                    "genre": item.render_genre(), 
                    "vote_avg": item.render_vote_average(), 
                    "vote_count": item.vote_count, 
                    "poster": item.render_poster(),
                    "slug": item.slug,
                    "type": "serie" 
                    })

            # Get the user's watchlist content (series only here)
            user_watchlist_series = set(
                WatchList.objects.filter(
                    user=request.user.id, serie__isnull=False, 
                ).values_list("serie_id", flat=True)
            )

            # Get the user's like content
            user_liked_series = set(
                Like.objects.filter(
                    user=request.user.id, content_type="serie"
                ).values_list("object_id", flat=True)
            )

            context = {
                'page_obj' : page_obj,
                'sort_by': sort_by,
                'query_pagin_url': query_pagin_url,
                'query_sort_url': query_sort_url,
                'current_order': sel_order,
                'base_url': base_url,
                'list_media' : list_media,
                'user_liked_series': user_liked_series,
                'user_watchlist_series': user_watchlist_series,
            }

            # Temporary placement for paginator design
            context["desktop_pages"] = page_window(
                page_obj.number, # current page number
                page_obj.paginator.num_pages, # total amount of pages
                size=5 # amount of buttons to display around current page
            )

            context["mobile_pages"] = page_window(
                page_obj.number,
                page_obj.paginator.num_pages,
                size=2
            )

            # If user select a sort-by or page parameter, create a request with HTMX
            if request.headers.get('HX-request'):
                print("\n -- HTMX request detected - returning partial list --")
                return render(request, 'partials/media_list.html', context=context)

            return render(request, 'serie/list_serie.html', context=context)

        else:
            # if the serie does not exist in the database
            messages.error(request, "No Tv-Show found in the database")
            return redirect('main:home')

    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")
        return redirect('main:home')


@timer
@num_queries
def serie_detail(request, slug):
    '''
    - get the serie object from the database using the serie_id=serie.id parameter in the URL request.
    - Check if logged user has a watchlist or like entry with this serie
    - add the comment form and list entries with reference to that Serie. 
    '''
    try:
        if Serie:
            # retrieve the specified serie requested by user
            # Get the seasons and episodes related to the serie
            serie = get_object_or_404(Serie, slug=slug)
            # seasons = serie.seasons.all().prefetch_related("episodes")
            seasons = serie.seasons.all()

            # Show the cast of season 1 as main casting of the serie to display
            main_cast = None
            for season in seasons:
                if season.season_number == 1:
                    main_cast = season.casting
                    break

            print(f"main_casting: {main_cast}")
            print(f"serie {serie.title} contains: {len(seasons)} seasons")

            # get the comments related to the serie
            comments = serie.comments.all()
            
            print(f"number of comments: {len(comments)}")

            form = CommentForm()
            context = {
                'serie': serie,
                'seasons': seasons,
                'form': form,
                'main_cast': main_cast,
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
                        "user_liked_serie": user_liked_serie,
                        "user_watchlist_series": user_watchlist_series,
                        "form": form,
                    }
                )

            return render(request,'serie/detail_serie.html', context=context)

        # if the serie does not exist in the database
        else:
            messages.error(request, "No Tv Show found in the database with this title")
            print(f" error : Serie model not found in the database")
            return redirect('serie:list_serie')

    except Exception as e:
        messages.error(request, "the page seem to experience some issue, please try again later")
        print(f" error :{e}\n")
        return redirect('main:home')


@timer
@num_queries
def load_season_data(request, season_id):
    '''
    Will pass the season data being requested via HTMX.
    Prevent detail_serie view from overloading too much content at once in the DOM.
    '''
    print(" i arrived here !! ")
    # get the correct season
    season = Season.objects.get(id=season_id)
    print(f"seasons: {season}")
    # get the data and episodes from it

    episode_content = season.episodes.all()

    # episode_content = Episode.objects.filter(season_id=season_id).only(
    #     "title", "number", "overview", "release_date", "v"
    # )

    print(f" season_content: {episode_content} \n")

    episode = None
    episode_card = []

    for item in episode_content:
        episode_card.append({
            # "id": item.pk, 
            "title": item.title,
            "number": item.episode_number,
            # "episode": item.episode_number,
            "overview": item.overview,
            'release_date': item.render_release_date(),
            "length": item.render_length(), 
            # "vote_avg": item.render_vote_average(), 
            # "vote_count": item.vote_count, 
            "banner": item.render_banner(),
            # "slug": item.slug,
            })

    context = {
        'episode_card': episode_card,
        'season': season,
    }

    print("I am now there")
    return render(request, 'serie/partials/season_content.html', context=context )
