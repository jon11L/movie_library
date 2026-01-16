from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, IntegerField

import time

from .filters import SharedMediaFilter
from movie.models import Movie
from serie.models import Serie
from user_library.models import Like, WatchList


# Temporary placement for paginator design
from core.tools.paginator import page_window

# ----- Need to fix Bug if user only put space char in title, then all Movie&Serie pass through filter -------
def search(request):
    """
    View function for search page
    - request.method == 'GET' and not request.GET -> render the filter landing page
    - if request.method == 'GET' and request.GET -> user search with Filtering system
    or from search bar (title filter only)
    """
    # Initialize variables with empty values
    start_time = time.time()
    total_found = 0
    user_liked_movies = set()
    user_liked_series = set()
    user_watchlist_movies = set()
    user_watchlist_series = set()

    results = [] # Will hold the mixed list query (Movie+Serie)

    # Determine which content type to display, Default to 'all'
    content_type = request.GET.get('content_type', 'all')

    # Check if any filter parameters have values
    has_filter_values = False
    print(f"items from the get request:\n\n {request.GET.items()}")

    for key, value in request.GET.items():
        print(f"key'{key}' :  value '{value}'")
        if value and key not in ['page', 'csrfmiddlewaretoken', 'content_type'] and value.strip() != "":
            # Means some filtering value were passed other than default request value
            has_filter_values = True
            if value.strip() == "":
                has_filter_values = False
            break

    print(f"\n--has_filter_values: {has_filter_values}")

    # Render/Initialize the filter form (without queryset)
    Media_filter = SharedMediaFilter(request.GET)
    print(f"-- content_filter: {Media_filter}\n")

    # ----- Initial search page load, no query/filter/ done yet-----
    if request.method == 'GET' and not request.GET:
        print("\n-- going to search page --")

        context = {'filter': Media_filter}
        return render(request, 'search/search.html', context=context)

    # -- Handle GET requests with parameters //
    #  user's action from the Filter Form Button (the search page)
    if request.method == 'GET' and request.GET:
        print("\n-- User submit a filtered search --")

        #  when no filters are selected; return only the filter form
        if not has_filter_values :
            print("-- no filter values applied --")

            context = {
                'filter': Media_filter,
            }

        else: # Filter values are applied.
            print("-- filter values applied --")# debug print
            filtered_movies = []
            filtered_series = []

            title_value = request.GET.get("title", "").strip()

            # Apply the filters to the Movie and Serie models if 'all' selected or specific content type
            if content_type in ['movie', 'all']:
                movie_filter = SharedMediaFilter(
                    request.GET,
                    queryset=Movie.objects.only(
                        "id",
                        "title",
                        "genre",
                        "slug",
                        "poster_images",
                        "vote_average",
                        "vote_count",
                    ),
                )
                filtered_movies = movie_filter.qs
                # print(f"Filtered movies: {len(filtered_movies)}")

                if title_value:
                    # Create a relevance system by Title: exact->startwith->remaining.
                    filtered_movies = filtered_movies.annotate(
                        relevance=Case(
                            # exact match
                            When(title__iexact=title_value, then=Value(1)),
                            # startswith
                            When(title__istartswith=title_value, then=Value(2)),
                            # contains (already filtered)
                            default=Value(3),
                            output_field=IntegerField(),
                        )
                    ).order_by("-relevance", "title")

            if content_type in ['serie', 'all']:
                serie_filter = SharedMediaFilter(
                    request.GET,
                    queryset=Serie.objects.only(
                        "id",
                        "title",
                        "genre",
                        "slug",
                        "poster_images",
                        "vote_average",
                        "vote_count",
                    ),
                )
                filtered_series = serie_filter.qs
                # print(f"Filtered series: {len(filtered_series)}")

                if title_value:
                    # Same process for the series
                    filtered_series = filtered_series.annotate(
                        relevance=Case(
                            When(title__iexact=title_value, then=Value(1)),
                            When(title__istartswith=title_value, then=Value(2)),
                            default=Value(3),
                            output_field=IntegerField(),
                        )
                    ).order_by("-relevance", "title")

            # Combine both queries into one for sorting
            # even if evaluation done before paginating/limiting and normalizing
            combined = (list(filtered_movies) + list(filtered_series))

            # Sort the media found by relevance to group Movie and Serie.
            #  Won't no longer need if creating a common Media model.Neither 'combined'
            if title_value:
                results = sorted(
                    combined,
                    key=lambda x: (getattr(x, "relevance", 0), getattr(x, "title", "")),
                    reverse=False,
                )
            else:
                results = sorted(
                    combined,
                    key=lambda x: x.title,
                    reverse=False,
                )

            print("\n", results[0:5], "\n")
            total_found = len(results)
            print(
                f"\n-- Total found {total_found}: "
                f"{len(filtered_movies)} movies -- {len(filtered_series)} series --\n"
            )

            # -- paginate over the results --
            paginator = Paginator(results, 24)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(f"-- List content: {page_obj}")

            list_media = []
            for item in page_obj:
                list_media.append({
                    "title": item.title, 
                    "id": item.pk, 
                    "genre": item.render_genre(), 
                    "vote_avg": item.render_vote_average(), 
                    "vote_count": item.vote_count, 
                    "poster": item.render_poster(),
                    "slug": item.slug,
                    "type": "movie" if isinstance(item, Movie) else "serie"
                    })

            # Preserve all GET parameters except 'page' for the Paginator system
            query_params = request.GET.copy()
            print(f"-- Query params: {query_params}\n")  # Debug print
            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')

            # Allow to keep the query parameter in the url for pagination
            query_string_url = query_params.urlencode()

            context = {
                'filter': Media_filter,
                'query_params': query_params,
                'query_url': query_string_url,
                'list_media': list_media,
                'page_obj': page_obj,
                'total_found': total_found if total_found > 0 else None,
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
                # Get the user's watchlist and like content (movies, series)

                user_watchlist_movies = set(
                    WatchList.objects.filter(
                        user=request.user.id, movie__isnull=False
                        ).values_list('movie_id', flat=True)
                )

                user_watchlist_series = set(
                    WatchList.objects.filter(
                        user=request.user.id, serie__isnull=False
                    ).values_list('serie_id', flat=True)
                )

                # Get the user's liked content (movies, series)
                user_liked_movies = set(
                    Like.objects.filter(
                        user=request.user.id, content_type='movie'
                    ).values_list('object_id', flat=True)
                )

                user_liked_series = set(
                    Like.objects.filter(
                        user=request.user.id, content_type='serie'
                        ).values_list('object_id', flat=True)
                )

                context.update(
                    {
                    'user_liked_movies': user_liked_movies,
                    'user_liked_series': user_liked_series,
                    'user_watchlist_movies': user_watchlist_movies, 
                    'user_watchlist_series': user_watchlist_series, 
                    }
                )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"-- processing page time: {elapsed_time:.2f} seconds. --\n")
        return render(request, 'search/search.html', context=context)
