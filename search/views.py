from django.shortcuts import render, redirect
from django.core.paginator import Paginator

import time

from .filters import SharedMediaFilter
from movie.models import Movie
from serie.models import Serie
from user_library.models import Like, WatchList


# ----- Need to fix Bug if user only put space char in title, then all Movie&Serie pass through filter -------
def search(request):
    """
    View function for search page
    - request.method == 'GET' and not request.GET -> render the filter landing page
    - if request.method == 'GET' and request.GET -> user search with Filtering system
    or from search bar (title filter only)
    """
    # Initialize with empty values
    movies = []
    series = []
    search_query = ""
    total_found = 0
    user_liked_movies = set()
    user_liked_series = set()
    user_watchlist_movies = set()
    user_watchlist_series = set()

    results = []
    start_time = time.time()

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

    print(f"\n--has_filter_values: {has_filter_values}")  # Debug print

    # Render/Initialize the filter form (without queryset)
    Media_filter = SharedMediaFilter(request.GET)
    print(f"content_filter: {Media_filter}")  # Debug print

    # ----- Initial search page load, user reach the search page without any query/filter/request -----
    if request.method == 'GET' and not request.GET:
        print("going to search page") # debug print

        context ={'filter': Media_filter}
        return render(request, 'search/search.html', context=context)

    # Handle GET requests with parameters // action from the Filter Form Button (in the search page)
    if request.method == 'GET' and request.GET:
        print("-- User submit a filtered search --") # debug print

        #  when no filters are selected; return only the filter form
        if not has_filter_values :
            print("no filter values applied")
            
            context = {
                'filter': Media_filter,
                'filters_applied': False  # Flag to show a message in the template
            }

        else: # Filter values are applied.
            print("filter values applied")# debug print
            filtered_movies = []
            filtered_series = []

            # Apply the filters to the Movie and Serie models if 'all' selected or specific content type
            if content_type in ['movie', 'all']:
                movie_filter = SharedMediaFilter(request.GET, queryset=Movie.objects.only("id", "slug", "poster_images", "title" , "vote_average"))
                filtered_movies = movie_filter.qs
                # print(f"Filtered movies: {filtered_movies}")

            if content_type in ['serie', 'all']:
                serie_filter = SharedMediaFilter(request.GET, queryset=Serie.objects.only("id", "slug", "poster_images", "title", "vote_average"))
                filtered_series = serie_filter.qs
                # print(f"Filtered series: {filtered_series}")

            for movie in filtered_movies:
                results.append({
                    'object': movie,
                    'type': 'movie',
                })

            for serie in filtered_series:
                results.append({
                    'object': serie,
                    'type': 'serie',
                })

            results = sorted(results, key=lambda x: x['object'].title, reverse=False)

            total_found = len(results)
            print(f"Total found: {total_found}. {len(filtered_movies)} movies and {len(filtered_series)} series")  # Debug print

            # -- paginate over the results --
            paginator = Paginator(results, 24)
            page_number = request.GET.get('page')
            page_object = paginator.get_page(page_number)
            print(f"List content: {page_object}")

            # Preserve all GET parameters except 'page' for the Paginator system
            query_params = request.GET.copy()
            print(f"Query params: {query_params}")  # Debug print
            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')
            
            # Allow to keep the query parameter in the url for pagination
            query_string_url = query_params.urlencode()

            context = {
                'filter': Media_filter,
                'query_params': query_params,
                'query_url': query_string_url,
                'list_content': page_object,
                'total_found': total_found if total_found > 0 else None,
                'filters_applied': True
            }

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
        print(f"\ntime: {elapsed_time:.2f} seconds.\n")
        return render(request, 'search/search.html', context=context)