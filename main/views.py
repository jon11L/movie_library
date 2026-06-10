import datetime
import traceback

from django.shortcuts import render, redirect
from django.contrib import messages
# from django.http import JsonResponse
# from django.contrib.auth.decorators import user_passes_test

from core.context import get_user_watchlist,  get_user_review
from core.tools.wrappers import timer, num_queries
# models
from media_library.models import Media
from review.models import Review
from watchlist.models import WatchList
# tooling
from review.forms import ReviewForm
from watchlist.forms import WatchListForm

# def admin_check(user):
#     return user.is_superuser  # or user.is_staff for staff users


def about_page(request):
    return render(request, "main/about.html")


@timer
@num_queries
def home(request):
    """
    Home landing page.\n
    Display some of latest content
    (Movies and Series) up to 6-8 randomly selected for each.
    - Recently released.
    - coming up soon.
    - Random pick
    - from user Watchlist
    - coming back (Series only)
    - generally added to watchlist
    """

    # initialize variables
    list_media_ids = set()  # to track the media ids already included in the context, to avoid duplicates.
    user_reviews = set()
    user_watchlist = set()
    # list of the sample media being displayed
    recent_movies = None
    upcoming_movies = None
    random_movies = None
    ongoing_series = None
    new_series = None
    random_series = None
    movies_count = None
    series_count = None

    try:
        # to display movies & series that are coming soon or recently released
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)  # yesterday
        tomorrow = today + datetime.timedelta(days=1)  # tomorrow
        week_ago = today - datetime.timedelta(days=7)  # 7 days ago
        week_later = today + datetime.timedelta(days=7)  # 7 days later
        fortnight_ago = today - datetime.timedelta(days=14)  # 2 weeks ago
        bi_week_later = today + datetime.timedelta(days=14)  # 2 weeks later
        month_ago = today - datetime.timedelta(days=30)  # 30 days ago
        week_start = today - datetime.timedelta(
            days=today.weekday()
        )  # Monday of the current week
        week_end = week_start + datetime.timedelta(days=6)  # Sunday of the current week



        # display the amount of Movies & Series available from the database
        series_count = Media.objects.filter(media_type='serie').count()
        movies_count = Media.objects.filter(media_type='movie').count()
        # movies_count = Movie.objects.exclude(is_active=False).count()

        # --- Prepare various content lists (eg: recently released, coming soon, etc.) ---
        # and return a sample of it / 6 per selections.

        # recently released movies (in the last 2 weeks)
        recent_movies = (
            Media.objects.filter(
                media_type="movie",
                release_date__range=(fortnight_ago, today),
                movie__length__gte=45,
            )
            .only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )
            .exclude(adult=True)
            .order_by("?")[:12]
        )

        # retrieve the movies coming out soon.
        upcoming_movies = (
            Media.objects.filter(
                media_type="movie",
                release_date__range=(tomorrow, bi_week_later),
                movie__length__gte=45,
            )
            .only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )
            .exclude(adult=True)
            .order_by("?")[:12]
        )

        random_movies = (
            Media.objects.filter(media_type="movie", movie__length__gte=45)
            .only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )
            .exclude(is_active=False)
            .order_by("?")[:12]
        )


        ongoing_series = (
            Media.objects.filter(
                media_type="serie", release_date__range=(fortnight_ago, week_later)
            )
            .only(
                "id",
                "title",
                "genre",
                "vote_average",
                "vote_count",
                "poster_images",
                "slug",
            )
            .order_by("?")[:12]
        )



        new_series = (
            Media.objects.filter(
                media_type='serie',
                release_date__range=(fortnight_ago, bi_week_later)
            )
            .only("id", "title", "genre", "vote_average", "vote_count", "poster_images", "slug")
            .order_by("?")[:12]
        )


        # Perhaps remove later and create a one Random pick media sample
        random_series = Media.objects.filter(media_type='serie').only(
            "id", "title", "genre", "vote_average", "vote_count", "poster_images", "slug"
        ).order_by("?")[:12] 


        # ------ add side content , from other user's Watchlist or like movies/series ------
        discover_media = []  # list to hold the media saved in watchlist from other users
        # discover_list = None  # list to hold the user ids already processed
        if request.user.is_authenticated:
            discover_list = WatchList.objects.exclude(user=request.user).order_by("?")[
                :12
            ].select_related("media") 
        else:
            # list to hold any watchlist instances
            discover_list = WatchList.objects.all().order_by("?")[:12].select_related("media")


        # load some item saved in watchlist by different users.
        for item in discover_list:
            media_obj = item.media
            if media_obj:
                discover_media.append({
                    "title": media_obj.title, 
                    "id": media_obj.pk, 
                    "genre": media_obj.render_genre(), 
                    "render_vote_average": media_obj.render_vote_average(), 
                    "vote_count": media_obj.vote_count, 
                    "render_poster": media_obj.render_poster(),
                    "slug": media_obj.slug,
                    "type": media_obj.media_type,
                    })
                # list_media_ids.add(media_obj.pk)

        # print(f"discover_media: {discover_media[0:2]}\n") # debug print

        # Display the watchlist form in the modal When user click
        watchlist_form = WatchListForm() 
        review_form = ReviewForm() 

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
            'watchlist_form': watchlist_form,
            'review_form': review_form
        }

        if request.user.is_authenticated:
            # --------- Get the user's watchlist content (movies, series)  -----------
            user = request.user
            # print(f"user: {user}\n")  # debug print

            watchlist = WatchList.objects.filter(user=user).select_related("media")
            print(f"user's Watchlist:\n{watchlist[:3]}...\n")  # debug print

            watchlist_media = []
            # initialize the list watchlist sample
            for item in watchlist.order_by("?")[:12]:
                media_obj = item.media
                if media_obj:
                    watchlist_media.append({
                        "title": media_obj.title, 
                        "id": media_obj.pk, 
                        "genre": media_obj.render_genre(), 
                        "render_vote_average": media_obj.render_vote_average(), 
                        "vote_count": media_obj.vote_count, 
                        "render_poster": media_obj.render_poster(),
                        "slug": media_obj.slug,
                        "type": media_obj.media_type,
                        })

            # Collect the media ids to check if user has watchlist or reviews
            for qs in (recent_movies, upcoming_movies, random_movies, 
                       ongoing_series, new_series, random_series):
                list_media_ids.update(media.pk for media in qs)

            list_media_ids.update(media["id"] for media in discover_media)
            list_media_ids.update(media["id"] for media in watchlist_media)
            print(f"\n --length media: {len(list_media_ids)}\n")

                # -------- Check if the user media exist in the watchlist/review of current user --------
            user_watchlist = get_user_watchlist(request.user.pk, media_ids=list_media_ids)
            user_reviews = get_user_review(request.user.pk, media_ids=list_media_ids)

            context.update(
                {
                    "user_reviews": user_reviews,
                    "user_watchlist": user_watchlist,
                    "watchlist_content": watchlist_media,
                }
            )

        return render(request, "main/home.html", context=context)

    except Exception as e:
        # use traceback to get more details about the error
        traceback.print_exc()

        print(f"An error occurred while loading the homepage: {e}\n")
        messages.error(request, "An error occurred while loading the page.")
        return redirect(to="user:login")
