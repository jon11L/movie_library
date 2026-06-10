from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework import viewsets
from rest_framework import generics, filters

from core.context import get_user_watchlist,  get_user_review
from core.permissions import IsAdminOrIsAuthenticatedReadOnly
from core.tools.paginator import page_window # Temporary placement for paginator design
from core.tools.wrappers import timer, num_queries
from core.throttle import AdminRateThrottle, UserBurstThrottle, UserSustainThrottle, UserDayThrottle
from rest_framework.throttling import AnonRateThrottle

# from .serializers import MediaListSerializer, MediaDetailSerializer
# models
from .models import Media, Season
from comment.models import Comment
from review.models import Review
from watchlist.models import WatchList
# forms
from comment.forms import CommentForm
from watchlist.forms import WatchListForm
from review.forms import ReviewForm


# def admin_check(user):
#     return user.is_superuser  # or user.is_staff for staff users


# class MovieViewSet(viewsets.ModelViewSet):
#     '''View to serialize Movie model'''
#     # authentication_classes = [SessionAuthentication, BasicAuthentication]
#     queryset = Movie.objects.all().order_by('-id')
#     serializer_class = MovieSerializer
#     permission_classes = [IsAdminOrIsAuthenticatedReadOnly]


# =============== API views ===================
# class MovieListView(generics.ListCreateAPIView):
#     # queryset = Movie.objects.all().order_by('-id')
#     queryset = Movie.objects.select_related().prefetch_related()

#     serializer_class = MovieListSerializer
#     permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     search_fields = ['title', "genre"]
#     ordering_fields = ['release_date', "vote_average"]
#     throttle_classes = [
#         AnonRateThrottle,
#         AdminRateThrottle,
#         UserBurstThrottle,
#         UserSustainThrottle,
#         UserDayThrottle,
#     ]


# class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Movie.objects.all()
#     serializer_class = MovieDetailSerializer
#     permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
#     throttle_classes = [
#         AnonRateThrottle,
#         AdminRateThrottle,
#         UserBurstThrottle,
#         UserSustainThrottle,
#         UserDayThrottle,
#     ]

# ======= Regular template views ==================
@timer
@num_queries
def media_list(request, media_type):
    '''retrieve the movies from newer to older and display them in the template
    page's goal is to display up to 24 content pieces per page
    '''
    base_url = f'/media_library/{media_type}'

    list_media = [] # list to hold the content (movies, series)
    sort_by = None
    user_watchlist = set()
    user_reviews = set()
    list_media_ids = set() # to track the media ids being displayed and correlate with user data, to avoid larger queries.

    try:
        if Media:

            # ========== setting values for the sorting-by feature ==========================
            sort_by = (
                # ('display name', 'django field')
                ('first added', 'id'),
                ('last added', '-id'),
                ('A-z title', 'title'), 
                ('Z-a title', '-title'),
                ('newest first', '-release_date'), 
                ('oldest first', 'release_date'),
                ('least popular', 'popularity'),
                ('most popular', '-popularity'),
                ('least voted', 'vote_count'),
                ('most voted', '-vote_count'),
                ('lowest rating', 'vote_average'),
                ('highest rating', '-vote_average'),
            )

            query_params = request.GET.copy()
            print(f"-- Query params: {query_params}\n")  # Debug print

            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')
            # Allow to keep the query parameter in the url for pagination
            query_pagin_url = query_params.urlencode()

            sel_order = '-id' # default selection order / first reach of the list page
            # if user select a sort-by option, update the selection order for the query
            if 'order_by' in query_params:
                sel_order = query_params.get('order_by')
            print(f"selected order: {sel_order}")
            # send the url parameters for sort-by, to keep the selection when user change page
            query_sort_url = query_params.urlencode() 

            # list_fields = ["id",
            #             "title",
            #             "genre",
            #             "release_date",
            #             "popularity",
            #             "vote_average",
            #             "vote_count",
            #             "poster_images",
            #             "slug",
            #             "media_type",
            #             ]

            if media_type == 'movies':

                media = (
                    Media.objects.filter(media_type="movie")
                    .only(
                        "id",
                        "title",
                        "genre",
                        "release_date",
                        "popularity",
                        "vote_average",
                        "vote_count",
                        "poster_images",
                        "slug",
                        "media_type",
                    )
                    .exclude(is_active=False)
                    .exclude(release_date__isnull=True)
                    .exclude(
                        movie__length__range=(1, 45)
                    )  # how to remove them with media as they are in the child model Movie
                    # .order_by(f"{sel_order}")
                )

            elif media_type == 'series':

                media = (
                    Media.objects.filter(media_type='serie').only(
                        "id",
                        "title",
                        "genre",
                        "release_date",
                        "popularity",
                        "vote_average",
                        "vote_count",
                        "poster_images",
                        "slug",
                        "media_type",

                    )
                    .exclude(is_active=False)
                    .exclude(release_date__isnull=True)
                    # .exclude(movie__length__range=(1, 45)) # how to remove them with media as they are in the child model Movie
                    # .order_by(f"{sel_order}")
                )

            elif media_type == "documentaries":
                # Check in Media if genre contains 'documentary' then load them for templating
                media = (
                    Media.objects.filter(genre__icontains="documentary")
                    .only(
                        "id",
                        "title",
                        "genre",
                        'release_date',
                        'popularity',
                        "vote_average",
                        "vote_count",
                        "poster_images",
                        "slug",
                        "media_type",
                    )
                    .exclude(is_active=False)
                    # .order_by("-vote_count")
                )

            elif media_type == "short-films":
                # Check if they are short Movies under 45 minutes
                media = (
                    Media.objects.filter(media_type='movie', movie__length__range=(0, 44))
                    .only(
                        "id",
                        "title",
                        "genre",
                        'release_date',
                        'popularity',
                        "poster_images",
                        "vote_average",
                        "vote_count",
                        "slug",
                        "media_type",
                    )
                    .exclude(is_active=False)
                    .order_by("-vote_count")
                )  # length between 0 and 45 minutes

            elif media_type == "animes":
                # Check if they are Anime Movies and Series
                media = (
                    Media.objects.filter(genre__icontains="Animation")
                    .only(
                        "id",
                        "title",
                        "genre",
                        'release_date',
                        'popularity',
                        "poster_images",
                        "vote_average",
                        "vote_count",
                        "slug",
                        "media_type",
                    )
                    .exclude(is_active=False)
                    # .order_by("-vote_count")
                )

            media = media.order_by(sel_order)

            # paginates over the pre loaded query
            paginator = Paginator(media, 24)
            # Get the current page number from the GET request
            page = request.GET.get('page')
            page_obj = paginator.get_page(page)
            print(f"\n-- {page_obj} --\n")

            # create a standardized data stack to pass in templates.
            # Avoiding any extra hidden queries on the frontend
            for item in page_obj:
                list_media.append({
                    "id": item.pk, 
                    "title": item.title,
                    # "release_date": item.release_date.year, 
                    "genre": item.render_genre(), 
                    "render_vote_average": item.render_vote_average(), 
                    "vote_count": item.vote_count, 
                    "render_poster": item.render_poster(),
                    "slug": item.slug,
                    "type": item.media_type,
                    })
            # print(list_media[0:2], '\n')

            # present the watchlist and review form in the modal,
            #  when not logged in, will display a message to invite user to register/log in
            watchlist_form = WatchListForm() 
            review_form = ReviewForm() 

            context = {
                'page_obj' : page_obj,
                'sort_by': sort_by, # the list of sorting-by option
                'query_pagin_url': query_pagin_url, # send the url parameters for pagination
                'query_sort_url': query_sort_url, # send the url parameters for sort-by
                'current_order': sel_order,
                'base_url': base_url,
                'list_media': list_media,
                "media_type": media_type.capitalize(),
                'watchlist_form': watchlist_form,
                'review_form': review_form,
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

            if request.user.is_authenticated:
                # Collect the media ids to check if user has watchlist or reviews
                list_media_ids.update(media["id"] for media in list_media)

                user_watchlist = get_user_watchlist(request.user.pk, media_ids=list_media_ids)
                user_reviews = get_user_review(request.user.pk, media_ids=list_media_ids)

                context.update(
                    {
                        'user_reviews': user_reviews,
                        'user_watchlist': user_watchlist,
                    }
                )

            # If user select a sort-by or page parameter, create a request with HTMX
            if request.headers.get('HX-request'):
                print("\n -- HTMX request detected - returning partial list --")
                return render(request, 'partials/media_grid.html', context=context)

            return render(request, 'media_library/list_media.html', context=context)

        else:
            messages.error(request, 'Error, or No media found in the database.')
            return redirect('main:home')

    except Exception as e:
        messages.error(request, "the page seems to experience some issue, please try again later")
        print(f" error :\n{e}")
        return redirect('main:home')


@timer
@num_queries
def media_detail(request, slug):
    '''
    - get the media object from the database using the pk parameter in the URL request.
    \n
    - Check if logged user has a watchlist or like entry with this Media
    - add the comment form and list entries with reference to that Media. 
    '''
    try:
        if Media:
            media = Media.objects.select_related("movie", "serie").get(slug=slug)

            # get the comments related to the media
            comments = media.comments.all().order_by('-created_at')
            print(f"\nNumber of comments: {(comments.count())}")

            comment_form = CommentForm() # present the Comment block form
            # present the watchlist form in the modal When user click 
            watchlist_form = WatchListForm() 
            review_form = ReviewForm()

            context = {
                'media': media,
                'comments': comments,
                'form': comment_form,
                'watchlist_form': watchlist_form,
                'review_form': review_form,
                }

            # Prepare part if the media requested is a serie or movie
            # load different content
            if media.media_type == 'movie':
                print("type is Movie")
                # context['movie'] = media.movie
                context['length'] = media.movie.render_length()
                context['casting'] = media.movie.casting
                context['director'] = media.movie.render_director()
                context['writer'] = media.movie.render_writer()
                # fetch the data from media.movie

            # if it is a serie - preload the season data and episode
            elif media.media_type == 'serie':
                print("type is Serie")
                context['serie'] = media.serie
                context['created_by'] = media.serie.render_created_by()

                # load the seasons
                seasons = media.serie.seasons.all()
                # Show the cast of season 1 as main casting of the serie to display
                main_cast = None
                for season in seasons:
                    if season.season_number == 1:
                        main_cast = season.casting
                        # avg length create a new query, maybe can optimize
                        avg_episode_length = season.render_avg_episode_length()
                        break
                context['casting'] = main_cast
                context['seasons'] = seasons
                context['length'] = avg_episode_length

            # display the Comment form if user is connected
            if request.user.is_authenticated:
                # Get the user's watchlist content (movies, series)
                media_id = set()
                media_id.add(media.pk)

                # -------- Check if the user media exist in the watchlist/review of current user --------
                user_watchlist = get_user_watchlist(request.user, media_ids=media_id)
                user_reviews = get_user_review(request.user, media_ids=media_id)

                comment_form = CommentForm(request.POST or None) # here allow to post a comment.

                print(f"\nMedia In watchlist :{len(user_watchlist)}") # debug print

                context.update(
                    {
                        'form': comment_form,
                        'comments': comments,
                        'user_watchlist': user_watchlist,
                        'user_reviews': user_reviews,
                        
                    }
                )
            
            return render(request,'media_library/detail_media.html', context=context)

        else:
            messages.error(request, "No Media found in the database with this title")
            print(f"Media model not found in the database.")
            return redirect('movie:list_movie')

    except Exception as e:
        messages.error(
            request,
            "the media requested does not exist or the page experiences some issue, please try again later",
        )
        print(f" error :{e}")
        return redirect('main:home')


@timer
@num_queries
def load_season_data(request, season_id):
    '''
    Will pass the season data being requested via HTMX.
    Prevent detail_serie view from overloading too much content at once in the DOM.
    '''
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

    return render(request, 'media_library/partials/season_content.html', context=context )
