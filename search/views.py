from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, IntegerField

# tooling
from core.context import get_user_review, get_user_watchlist
from core.tools.paginator import page_window # Temporary placement for paginator design
from core.tools.wrappers import timer, num_queries
# models
from media_library.models import Media
from watchlist.models import WatchList
from review.models import Review

# forms and filters
from watchlist.forms import WatchListForm
from review.forms import ReviewForm
from .filters import MediaFilter


# def initialize_search(request):
#     """
#     View function to handle the initial search page load.
#     Renders the search page with the filter form and no results.
#     """
#     # Initialize the filter form without any queryset applied
#     Media_filter = MediaFilter()

#     context = {'filter': Media_filter}

#     return render(request, 'search/search.html', context=context)


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
    media_filter = None
    list_media = [] # list to hold the medias content (movies, series)

    user_watchlist = set() # initialize an empty set for user watchlist media IDs
    user_reviews = set() # initialize an empty set for user reviewed media IDs
    results = None # Will hold the final query mixed media list (Movie+Serie)
    list_media_ids = set()

    print(f"\n** search view called **\n")
    # Determine which content type to display, Default to 'all'
    content_type = request.GET.get('content_type', 'all')

    # Check if any filter parameters have values
    has_filter_values = False

    # if value passed in the request.GET, check if any of them have a value (not empty or whitespace)
    # if so, Means some filtering value were passed other than default request value,
    # activate the filtering system. Else has_filter_values remains False and the page will render only the filter form.
    for key, value in request.GET.items():
        print(f"key'{key}' :  value '{value}'")
        if value and key not in ['page', 'csrfmiddlewaretoken', 'content_type'] and value.strip() != "":
            has_filter_values = True
            break

    print(f"\n- has_filter_values: {has_filter_values} --")
    print(f"- items from the get request: {request.GET.items()}")

    # Render/Initialize the filter form (without queryset applied)
    media_filter = MediaFilter(request.GET)
    print(f"-- content_filter: {media_filter}\n")

    # --- Initial search page load, no filter applied / returns only the filter form ---
    if request.method == 'GET' and has_filter_values == False:
        
        print(
            "\n--clicked on navbar search btn  // going to search page // no filters values given"
            f"// -- Returns only the filter form.")
        context = {'filter': media_filter}

        return render(request, 'search/search.html', context=context)

    # -- Handle GET requests with parameters applied //
    #  user's action from the Filter Form Button (the search page) // or navbar search
    elif request.method == 'GET' and request.GET:
        print("\n-- User submit a filtered search // filter values applied --")

        # === setting values for sorting-by feature ===
        sort_by = (
            # ('display name', 'django field')
            ('A-z title', 'title'), 
            ('Z-a title', '-title'),
            ('first added', 'id'),
            ('last added', '-id'),
            ('oldest first', 'release_date'),
            ('newest first', '-release_date'), # release_date issue as serie is first_air_date
            ('least popular', 'popularity'),
            ('most popular', '-popularity'),
            ('least voted', 'vote_count'),
            ('most voted', '-vote_count'),
            ('lowest rating', 'vote_average'),
            ('highest rating', '-vote_average'),
        )

        filtered_media = None
        title_value = str(request.GET.get("title", "").strip())

        # Apply the filters to the Movie and Serie models if 'all' selected or specific content type
        # if content_type in ['movie', 'all']:
        filter = MediaFilter(
            request.GET,
            queryset=Media.objects.only(
                "id",
                "media_type",
                "title",
                'release_date',
                'popularity',
                "poster_images",
                "vote_average",
                "vote_count",
                "slug",
            ).prefetch_related("genres",),
        )
        filtered_media = filter.qs
        # better way to calculate reducing a query?
        movie_count = filtered_media.filter(media_type='movie').count()
        serie_count = filtered_media.filter(media_type='serie').count()

        total_found = movie_count + serie_count
        print(
            f"Filtered media search: {total_found} items found\n"
            f"-Movies: {movie_count}\n-Tv-Shows : {serie_count}"
            )

        # if search filtered done by title, apply a relevance system to sort the results
        if title_value and len(title_value) >= 2:
            # Create a relevance system by Title: exact->startwith->remaining.
            results = filtered_media.annotate(
                relevance=Case(
                    When(title__iexact=title_value, then=Value(1)), # exact match
                    When(title__istartswith=title_value, then=Value(2)), # title startswith
                    default=Value(3), # title in (already filtered)
                    output_field=IntegerField(),
                )
            ).order_by("relevance", "title")

            sel_order = 'title' # default to title when no sort-by given

        else:
            # if search given by other than title value
            results = filtered_media
            sel_order = '-id'

        # Preserve all GET parameters except 'page' for the Paginator system
        query_params = request.GET.copy()
        print(f"-- Query params: {query_params}\n")  # Debug print

        # Remove the 'page' parameter to avoid pagination issues
        if 'page' in query_params:
            query_params.pop('page')
        # Allow to keep the query parameter in the url for pagination
        query_pagin_url = query_params.urlencode()

        if 'order_by' in query_params:
            sel_order = query_params.get('order_by')
            print(f"selected order: {sel_order}")
            query_params.pop('order_by')
            results = filtered_media.order_by(sel_order)

        query_sort_url = query_params.urlencode()

        # print(f"\n--Results: {results[0:3]}...\n")

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
                "render_genre": item.render_genre(), 
                "render_vote_average": item.render_vote_average(), 
                "vote_count": item.vote_count, 
                "render_poster": item.render_poster(),
                "slug": item.slug,
                "type": item.media_type,
                })

        # Display watchlist form in the modal When user click
        watchlist_form = WatchListForm() 
        review_form = ReviewForm() 

        context = {
            'content_type': content_type,
            'page_obj': page_obj,
            'sort_by': sort_by,
            'filter': media_filter,
            # pagination & sorting urls to keep the query parameters in the url
            'query_pagin_url': query_pagin_url,
            'query_sort_url': query_sort_url,
            'current_order': sel_order,
            'base_url': base_url,
            'list_media': list_media, # 
            'query_params': query_params, # to recognize the filters applied // may have to ensure naming & value inside
            'total_found': total_found if total_found > 0 else None,
            'movie_count': movie_count if movie_count > 0 else 'no',
            'serie_count': serie_count if serie_count > 0 else 'no',
            'watchlist_form': watchlist_form,
            'review_form': review_form,
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

    # If user select a sort-by or page parameter, create a request with HTMX to update only the media list without reloading the page
    if request.headers.get('HX-request'):
        print("\n -- HTMX request detected - returning partial list --")
        return render(request, 'partials/media_grid.html', context=context)

    return render(request, 'search/search.html', context=context)
