from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, IntegerField

from core.tools.paginator import page_window # Temporary placement for paginator design
from core.tools.wrappers import timer, num_queries
from .filters import SharedMediaFilter
from movie.models import Movie
from serie.models import Serie
from user_library.models import Like, WatchList



@timer
@num_queries
def search(request):
    """
    View function for search page
    - request.method == 'GET' and not request.GET -> render the filter landing page / user fetch the search
    - if request.method == 'GET' and request.GET -> user search with Filtering system
    or from search bar (title filter only)
    - rquest.GET being the parameters being passed on for the filtering.
    """
    # Initialize variables with empty values
    total_found = 0
    sort_by = None
    base_url = "/search/"
    Media_filter = None
    list_media = [] # list to hold the medias content (movies, series)

    user_liked_movies = set()
    user_liked_series = set()
    user_watchlist_movies = set()
    user_watchlist_series = set()
    results = [] # Will hold the mixed list query (Movie+Serie)
    
    # Determine which content type to display, Default to 'all'
    content_type = request.GET.get('content_type', 'all')

    # Check if any filter parameters have values
    has_filter_values = False

    for key, value in request.GET.items():
        print(f"key'{key}' :  value '{value}'")
        if value and key not in ['page', 'csrfmiddlewaretoken', 'content_type'] and value.strip() != "":
            # Means some filtering value were passed other than default request value
            has_filter_values = True
            # can surely remove the if below as already checked above
            if value.strip() == "":
                has_filter_values = False
            break

    print(f"- has_filter_values: {has_filter_values} --")
    print(f"- items from the get request: {request.GET.items()}")

    # Render/Initialize the filter form (without queryset applied)
    Media_filter = SharedMediaFilter(request.GET)
    print(f"-- content_filter: {Media_filter}\n")

    # --- Initial search page load, no filter applied / returns only the filter form ---
    if request.method == 'GET' and has_filter_values == False:
        print("\n-- going to search page // no filters given // clicked on navbar search btn --")
        print(f"Returns only the filter form.")
        context = {'filter': Media_filter}

        return render(request, 'search/search.html', context=context)

    # -- Handle GET requests with parameters applied //
    #  user's action from the Filter Form Button (the search page) // or navbar search
    elif request.method == 'GET' and request.GET:
        print("\n-- User submit a filtered search // filter values applied --")

        # ===== when no filters are selected; return only the filter form ========
        # if not has_filter_values :
        #     print("-- no filter values applied // return page --")

        #     context = {
        #         'filter': Media_filter,
        #     }

        # ====== Filter values are applied. Filtering through Model ===========
        # print("-- ")# debug print
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
                    'release_date',
                    'popularity',
                    "poster_images",
                    "vote_average",
                    "vote_count",
                    "slug",
                ),
            )
            filtered_movies = movie_filter.qs
            # print(f"Filtered movies: {len(filtered_movies)}")

            if title_value:
                # Create a relevance system by Title: exact->startwith->remaining.
                filtered_movies = filtered_movies.annotate(
                    relevance=Case(
                        # title exact match
                        When(title__iexact=title_value, then=Value(1)),
                        # title startswith
                        When(title__istartswith=title_value, then=Value(2)),
                        # title in (already filtered)
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
                    'first_air_date',
                    'popularity',
                    "poster_images",
                    "vote_average",
                    "vote_count",
                    "slug",
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

        # === setting values for sorting-by feature ===
        sort_by = (
            # ('display name', 'django field')
            # ('newest first', '-release_date'), # release_date issue as serie is first_air_date
            # ('oldest first', 'release_date'),
            ('least popular', 'popularity'),
            ('most popular', '-popularity'),
            ('lowest vote', 'vote_count'),
            ('highest vote', '-vote_count'),
            ('A-z title', 'title'), 
            ('Z-a title', '-title'),
            ('first added', 'id'),
            ('last added', '-id'),
        )

        # create two query_urls parameters holder
        # one for the sort-by: without page and no order_by parameters
        # second for paginator: without page but keep order_by

        # Preserve all GET parameters except 'page' for the Paginator system
        query_params = request.GET.copy()
        print(f"-- Query params: {query_params}\n")  # Debug print
        # Remove the 'page' parameter to avoid pagination issues


        if 'page' in query_params:
            query_params.pop('page')
        # Allow to keep the query parameter in the url for pagination
        query_pagin_url = query_params.urlencode()
            

        sel_order = 'title' # default to title when no sort-by given
        if 'order_by' in query_params:
            sel_order = query_params.get('order_by')
            print(f"selected order: {sel_order}")
            query_params.pop('order_by')
        query_sort_url = query_params.urlencode()

        # Sort the media found by relevance to group Movie and Serie.
        #  Won't no longer need if creating a common Media model.Neither 'combined'
        if title_value:
            results = sorted(
                combined,
                key=lambda x: (getattr(x, "relevance", 0), getattr(x, "title", "")),
                reverse=False,
            )
        else:
            # Meaning a filter search based on other filtering value than title.
            results = sorted(
                combined,
                # key=lambda x: x.title,
                key=lambda x: getattr(x, sel_order.strip('-')),
                reverse=True if '-' in sel_order else False,
            )

        print(f"\n--Results: {results[0:3]}...\n")
        total_found = len(results)
        print(
            f"-- Total found {total_found}: "
            f"{len(filtered_movies)} movies -- {len(filtered_series)} series --\n" # Does this create a new query/evaluation
        )

        # -- paginate over the results --
        paginator = Paginator(results, 24)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(f"-- List content: {page_obj}")

        for item in page_obj:
            list_media.append({
                # Try to add release_date even if different fields from Movie & serie
                "title": item.title, 
                "id": item.pk, 
                "genre": item.render_genre(), 
                "vote_avg": item.render_vote_average(), 
                "vote_count": item.vote_count, 
                "poster": item.render_poster(),
                "slug": item.slug,
                "type": "movie" if isinstance(item, Movie) else "serie"
                })

        context = {
            'page_obj': page_obj,
            'sort_by': sort_by,
            'filter': Media_filter,
            'query_pagin_url': query_pagin_url,
            'query_sort_url': query_sort_url,
            'current_order': sel_order,
            'base_url': base_url,
            'list_media': list_media, # 
            'query_params': query_params, # to recognize the filters applied // may have to ensure naming & value inside
            'total_found': total_found if total_found > 0 else None,
        }

        #  ========== Temporary placement for paginator design ==============
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
    # If user select a sort-by or page parameter, create a request with HTMX
    if request.headers.get('HX-request'):
        print("\n -- HTMX request detected - returning partial list --")
        return render(request, 'partials/media_list.html', context=context)

    return render(request, 'search/search.html', context=context)
