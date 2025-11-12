from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

# from django.contrib.auth.decorators import user_passes_test
import datetime
import time
import random
import traceback

from movie.models import Movie
from serie.models import Serie
from user_library.models import Like, WatchList
from user.models import User


# def admin_check(user):
#     return user.is_superuser  # or user.is_staff for staff users


def about_page(request):
    return render(request, "main/about.html")


def home(request):
    """
    Home landing page. Display some of latest content
    (Movies and Series) up to 6 randomly selected each.
    - Recently released.
    - coming up soon.
    - Random pick
    - from user Watchlist
    - coming back (Series only)
    """
    start_time = time.time()

    try:
        # to display movies & series that are coming soon or recently released
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)  # yesterday
        week_ago = today - datetime.timedelta(days=7)  # 7 days ago
        fortnight_ago = today - datetime.timedelta(days=14)  # 2 weeks ago
        week_later = today + datetime.timedelta(days=7)  # 7 days later
        bi_week_later = today + datetime.timedelta(days=14)  # 2 weeks later
        month_ago = today - datetime.timedelta(days=30)  # 30 days ago
        week_start = today - datetime.timedelta(
            days=today.weekday()
        )  # Monday of the current week
        week_end = week_start + datetime.timedelta(days=6)  # Sunday of the current week

        recent_movies = None
        upcoming_movies = None
        random_movies = None
        ongoing_series = None
        new_series = None
        random_series = None
        movies_count = None
        series_count = None

        # Prepare various content lists (eg: recently released, coming soon, etc.)
        # and return a sample of it / 6 per selections.
        if Movie.objects.exists():
            # recently released movies (in the last 2 weeks)
            recent_movies = (
                Movie.objects.filter(
                    release_date__range=(fortnight_ago, yesterday), length__gte=45
                )
                .only("id", "title", "genre", "vote_average", "poster_images", "slug")
                .order_by("?")[:6]
            )

            # retrieve the movies coming out soon.
            upcoming_movies = (
                Movie.objects.filter(
                    release_date__range=(today, bi_week_later), length__gte=45
                )
                .only("id", "title", "genre", "vote_average", "poster_images", "slug")
                .order_by("?")[:6]
            )

            random_movies = (
                Movie.objects.filter(length__gte=45)
                .only("id", "title", "genre", "vote_average", "poster_images", "slug")
                .order_by("?")[:6]
            )
            print(f"- Random pick movies: {random_movies}")  # debug print

        # display the amount of Movies available from the database
        movies_count = Movie.objects.count()

        if Serie.objects.exists():

            ongoing_series = (
                Serie.objects.filter(last_air_date__range=(fortnight_ago, week_later))
                .only("id", "title", "genre", "vote_average", "poster_images", "slug")
                .order_by("?")[:6]
            )

            new_series = (
                Serie.objects.filter(
                    first_air_date__range=(fortnight_ago, bi_week_later)
                )
                .only("id", "title", "genre", "vote_average", "poster_images", "slug")
                .order_by("?")[:6]
            )

            random_series = Serie.objects.only(
                "id", "title", "genre", "vote_average", "poster_images", "slug"
            ).order_by("?")[
                :6
            ]  # retrieve 6 random movies from the last 30 days
            # print(f"- Random pick series: {random_series}\n")

            # display the amount of Movies & Series available from the database
            series_count = Serie.objects.count()

        # ------ add side content , from other user's Watchlist or like movies/series ------
        discover_media = []  # list to hold the content (movies, series)
        discover_list = None  # list to hold the user ids already processed
        # TODO:
        # Perhaps add prefetch related to optimize the queries here.
        # and select only needed fields from foreign key on serie and movie
        if request.user.is_authenticated:
            discover_list = WatchList.objects.exclude(user=request.user).order_by("?")[
                :3
            ]  # list to hold the user ids already processed
        else:
            discover_list = WatchList.objects.all().order_by("?")[
                :3
            ]  # list to hold the user ids already processed

        for item in discover_list:
            if item.movie:
                discover_media.append({"object": item.movie, "type": item.kind})
                # print(f"movie: {movie}\n") #debug print
            elif item.serie:
                discover_media.append({"object": item.serie, "type": item.kind})

        print(f"discover_media: {discover_media}\n")  # debug print

        # others_like = [] # list to hold the content (movies, series)
        # discover_like = None # list to hold the user ids already processed
        # if request.user.is_authenticated:
        #     discover_like = Like.objects.exclude(user=request.user).order_by("?")[:3] # list to hold the user ids already processed
        # else:
        #     discover_like = Like.objects.all().order_by("?")[:3] # list to hold the user ids already processed

        # for item in discover_like:
        #     if item.movie:
        #         others_like.append({
        #             'object': item.movie,
        #             'type': item.kind
        #             })
        #         # print(f"movie: {movie}\n") #debug print
        #     elif item.serie:
        #         others_like.append({
        #             'object': item.serie,
        #             'type': item.kind
        #             })

        # print(f"others_like: {others_like}\n") # debug print

        context = {
            "recent_movies": recent_movies,
            "movies_coming_soon": upcoming_movies,
            "random_movies": random_movies,
            "returning_series": ongoing_series,
            "new_series": new_series,
            "random_series": random_series,
            "discover_media": discover_media,
            "movies_count": movies_count,
            "series_count": series_count,
            # 'others_like': others_like,
        }

        if request.user.is_authenticated:
            # --------- Get the user's watchlist content (movies, series)  -----------
            user = request.user
            print(f"user: {user}\n")  # debug print

            watchlist = WatchList.objects.filter(user=user)
            print(f"user's Watchlist:\n{watchlist[:3]}...\n")  # debug print

            watchlist_content = []
            # initialize the list watchlist sample
            for item in watchlist.order_by("?")[:6]:
                # try:
                if item.movie:
                    watchlist_content.append({"object": item.movie, "type": item.kind})
                    # print(f"movie: {movie}\n") #debug print
                elif item.serie:
                    watchlist_content.append({"object": item.serie, "type": item.kind})

            user_watchlist_movies = set(
                watchlist.filter(movie__isnull=False).values_list("movie_id", flat=True)
            )

            user_watchlist_series = set(
                watchlist.filter(serie__isnull=False).values_list("serie_id", flat=True)
            )

            # -------- Get the user's like content (movies, series)  ----------
            user_liked_movies = set(
                Like.objects.filter(user=user, content_type="movie").values_list(
                    "object_id", flat=True
                )
            )

            user_liked_series = set(
                Like.objects.filter(user=user, content_type="serie").values_list(
                    "object_id", flat=True
                )
            )

            context.update(
                {
                    "user_liked_movies": user_liked_movies,
                    "user_liked_series": user_liked_series,
                    "user_watchlist_movies": user_watchlist_movies,
                    "user_watchlist_series": user_watchlist_series,
                    "watchlist_content": watchlist_content,
                }
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"time: {elapsed_time:.2f} seconds.")
        return render(request, "main/home.html", context=context)

    except Exception as e:
        # use traceback to get more details about the error
        traceback.print_exc()

        print(f"An error occurred while loading the homepage: {e}\n")
        messages.error(request, "An error occurred while loading the page.")
        return redirect(to="user:login")


def show_content(request, content):
    """
    Display the content media available in the database per style:
    - Documentaries
    - Short Films
    - Anime
    """
    start_time = time.time()
    media = []  # list to hold the content (movies, series)

    try:
        if content == "documentaries":
            # Check in Movies&Series if genre contains 'documentary' then load them for templating
            movies = Movie.objects.filter(genre__icontains="documentary").only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )

            series = Serie.objects.filter(genre__icontains="documentary").only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )

        elif content == "short films":
            # Check if they are short Movies under 45 minutes
            movies = Movie.objects.filter(length__lte=45, length__gt=0).only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )  # length between 0 and 45 minutes

            series = Serie.objects.none()  # No series for short content
        elif content == "anime":
            # Check if they are Anime Movies and Series
            movies = Movie.objects.filter(genre__icontains="Animation").only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )
            series = Serie.objects.filter(genre__icontains="Animation").only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )

        print(f"\n{content} has:\n{len(movies)} Movies\n{len(series)} Series:\n")
        # combine movies and series into a single list or object to pass in paginator
        if movies:
            for movie in movies:
                media.append(
                    {
                        "object": movie,
                        "type": "movie",
                    }
                )

        if series:
            for serie in series:
                media.append(
                    {
                        "object": serie,
                        "type": "serie",
                    }
                )

        # Sort the content media by title (ascending order)
        media = sorted(media, key=lambda x: x["object"].title, reverse=False)

        # -- paginate over the results --
        paginator = Paginator(media, 24)
        page_number = request.GET.get("page")
        page_object = paginator.get_page(page_number)
        print(f"Number of pages: {page_object}")  # debug print

        # Get the user's like content (movies, series)
        user_liked_movies = set(
            Like.objects.filter(user=request.user.id, content_type="movie").values_list(
                "object_id", flat=True
            )
        )

        user_liked_series = set(
            Like.objects.filter(user=request.user.id, content_type="serie").values_list(
                "object_id", flat=True
            )
        )

        # Get the user's watchlist content (movies, series)
        user_watchlist_movies = set(
            WatchList.objects.filter(
                user=request.user.id, movie__isnull=False
            ).values_list("movie_id", flat=True)
        )

        user_watchlist_series = set(
            WatchList.objects.filter(
                user=request.user.id, serie__isnull=False
            ).values_list("serie_id", flat=True)
        )

        # print(f"User's watchlist movies: {user_watchlist_movies}...\n")  # debug print
        # print(f"User's watchlist series: {user_watchlist_series}...\n")
        context = {
            "content": content.capitalize(),
            "movies": movies,
            "series": series,
            "list_content": page_object,
            "user_liked_movies": user_liked_movies,
            "user_liked_series": user_liked_series,
            "user_watchlist_movies": user_watchlist_movies,
            "user_watchlist_series": user_watchlist_series,
        }

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"time: {elapsed_time:.2f} seconds.")
        return render(request, "main/short_doc_anime.html", context=context)

    except Exception as e:
        print(f"An error occurred while loading the documentaries page: {e}\n")
        messages.error(request, f"An error occurred while loading the page. {e}")
        return redirect(to="main:home")
