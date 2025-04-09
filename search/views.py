from django.shortcuts import render, redirect
from django.core.paginator import Paginator
# from django.db.models import Q
from .filters import SharedMediaFilter
from movie.models import Movie
from serie.models import Serie
from user_library.models import Like


# >>> Author.objects.filter(name__unaccent__lower__trigram_similar="Hélène")
# [<Author: Helen Mirren>, <Author: Hélène Joy>]



# ----- attempt using the django-filters module -------
def search(request):
    """
    View function for search page
    """

    # Initialize with empty values
    movies = []
    series = []
    search_query = ""
    total_found = 0
    user_liked_movies = []
    user_liked_series = []
    results = []

    # Determine which content type to display
    content_type = request.GET.get('content_type', 'all')

    # Check if any filter parameters have values
    has_filter_values = False
    for key, value in request.GET.items():
        if value and key not in ['page', 'csrfmiddlewaretoken', 'content_type']:
            has_filter_values = True
            break
    
    print(f"has_filter_values: {has_filter_values}")  # Debug print
    # Default to empty queryset if no filters applied
    # base_queryset = Movie.objects.all() if has_filter_values else Movie.objects.none()
    # movie_filters = SharedMediaFilter(request.GET, queryset=base_queryset)
    

    # Initialize the filter form (without queryset for form rendering)
    content_filter = SharedMediaFilter(request.GET)
    print(f"content_filter: {content_filter}")  # Debug print

    # ----- Initial search page load, user reach the search page without any query/filter/request -----
    if request.method == 'GET' and not request.GET:
        print("going to search page") # debug print

        context ={
            'filter': content_filter,
        }

        return render(request, 'search/search.html', context=context)

    # Handle GET requests with parameters // action from the Filter Form Button
    if request.method == 'GET' and request.GET:
        print("-- button in form query clicked --") # debug print

        #  when no filtes are selected; return only the filter form
        if not has_filter_values:
            print("no filter values applied")
            context = {
                'filter': content_filter,
                'filters_applied': False  # Flag to show a message in the template
                # 'filtered_movies': movie_filters.qs,  # This will be empty
            }
        
        else: # if filter values are applied
            print("filter values applied")# debug print
            filtered_movies = []
            filtered_series = []

            if content_type in ['movie', 'all']:
                movie_filter = SharedMediaFilter(request.GET, queryset=Movie.objects.all())
                filtered_movies = movie_filter.qs
                # print(f"Filtered movies: {filtered_movies}")

            if content_type in ['serie', 'all']:
                serie_filter = SharedMediaFilter(request.GET, queryset=Serie.objects.all())
                filtered_series = serie_filter.qs
                # print(f"Filtered series: {filtered_series}")

            # Get the user's liked content (movies, series)
            user_liked_movies = Like.objects.filter(
                                                user=request.user.id, content_type='movie'
                                                ).values_list('object_id', flat=True)
            user_liked_series = Like.objects.filter(
                                                user=request.user.id, content_type='serie'
                                                ).values_list('object_id', flat=True)
            
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

            total_found = len(results)
            print(f"Total found: {total_found}")  # Debug print

            # -- paginate over the results --
            paginator = Paginator(results, 12)
            page_number = request.GET.get('page')
            page_object = paginator.get_page(page_number)
            print(f"List content: {page_object}")

            # Preserve all GET parameters except 'page'
            query_params = request.GET.copy()
            print(f"Query params: {query_params}")  # Debug print
            # Remove the 'page' parameter to avoid pagination issues
            if 'page' in query_params:
                query_params.pop('page')

            context = {
                'filter': content_filter,
                'query_params': query_params,
                'list_content': page_object,
                'total_found': total_found,
                'user_liked_movies': user_liked_movies,
                'user_liked_series': user_liked_series,
                'filters_applied': True
                # 'filtered_movies': filtered_movies,
            }

        return render(request, 'search/search.html', context=context)

    # #----- Handle the search bar submission query --------
    # if request.method == 'POST':
    #     print("submit search button on navbar")
    #     # Get the search query from the form input and filter movies and series by the query.
    #     search_query = request.POST.get('search_query', "").lower().strip()

    #     # Search through media content: movies, series
    #     try:
    #         if search_query:
    #         # filtered_movies = movie_filters.qs
    #             movies = Movie.objects.filter(title__icontains=search_query)
    #             series = Serie.objects.filter(title__icontains=search_query)

    #             # Get the user's liked content (movies, series)
    #             user_liked_movies = Like.objects.filter(
    #                                                 user=request.user.id, content_type='movie'
    #                                                 ).values_list('object_id', flat=True)

    #             user_liked_series = Like.objects.filter(
    #                                                 user=request.user.id, content_type='serie'
    #                                                 ).values_list('object_id', flat=True)

    #             # print(f"Movie filters: {filtered_movies}") # debug print
    #             # print(f"Serie filters: {serie_filters}") # debug print
    #             print(f"\n movies: {movies}\n series: {series} ") # log print


    #             # results = movies, series  # Combine the two querysets
    #             print(f"Results: {results}")  # Debug print
                
    #             for movie in movies:
    #                 results.append({
    #                     'object': movie,
    #                     'type': 'movie',
    #                 })
                
    #             for serie in series:
    #                 results.append({
    #                     'object': serie,
    #                     'type': 'serie',
    #                 })

    #             print(f"Results: {results}")  # Debug print
    #             # -- paginate over the results --
    #             paginator = Paginator(results, 12)
    #             page_number = request.GET.get('page')
    #             page_object = paginator.get_page(page_number)
    #             print(f"List content: {page_object}")

    #             # # Preserve all GET parameters except 'page'
    #             # query_params = request.GET.copy()
    #             # if 'page' in query_params:
    #             #     query_params.pop('page')


    #             total_found = movies.count() + series.count()
    #             print(f"Total found: {total_found}")

    #             context = {
    #                 'results': results,
    #                 # 'query_params': page_object,
    #                 'list_content': page_object,
    #                 'movies': movies,
    #                 'series' : series,
    #                 'query': search_query,
    #                 'total_found': total_found,
    #                 'filters_applied': True,  # Flag to show a message in the template
    #                 'filter': content_filter,
    #                 'user_liked_movies': user_liked_movies,
    #                 'user_liked_series': user_liked_series
    #                 }
    #                 # 'filtered_movies': filtered_movies
    #             # return render(request,'search/search.html', context=context)
    #             return redirect('search:search', query=search_query, content_type=content_type)
            
    #         else:
    #             print(f"\n empty search query given... '{search_query}' ") # debug print

    #             context = {
    #                 # 'query': search_query,
    #                 'filters_applied': False,  # Flag to show a message in the template
    #                 'filter': content_filter,
    #                 }

    #             return render(request,'search/search.html', context=context)

        
        # except Exception as e:
        #     context = {
        #         'error_message': f'An error occurred: {str(e)}',
        #         'query': search_query,
        #     }
        #     return render(request, 'search/search.html', context=context)







# # ----- first attempt with Q feature   ------------------
# def search(request):
#     """
#     View function for search page
#     """

#     # Initialize with empty values
#     movies = []
#     series = []
#     search_query = ""
#     total_found = 0

#     movie_filters = MovieFilter(request.GET, queryset=Movie.objects.all())
    
#     if request.method == 'GET':

#         # Apply the filters to the queryset
#         context ={
#             # 'filter': movie_filters,
#             # 'filtered_movies': movie_filters.qs
#         }

#         return render(request, 'search/search.html', context=context)

#     if request.method == 'POST':
#         # Get the search query from the form input and filter movies and series by the query.
#         search_query = ""
#         search_query = request.POST.get('search_query', "").lower()

#         # serie_filter = SerieFilter(request.GET, queryset=Serie.objects.all())


#         # Get the  filters search parameters  
#         year_from = request.POST.get('year_from')
#         year_to = request.POST.get('year_to')
#         min_rating = request.POST.get('min_rating')
#         max_rating = request.POST.get('max_rating')


#         print(f"\nsearch query given: {search_query} ")
#         print(f"\nsearch: year from query given: {year_from} ")
#         print(f"\nsearch: year to query given: {year_to} ")
#         print(f"\nsearch: minimum Rating query given: {min_rating} ")

#         # Search through media content: movies, series
#         try:
#             # if search_query:
#             if search_query or year_from or year_to or min_rating:

#                 movie_filters = Q()
#                 serie_filters = Q()
                
#                 print("Working until now") # debug print

#                 if search_query:
#                     movie_filters &= Q(title__icontains=search_query)
#                     serie_filters &= Q(title__icontains=search_query)
                
#                 if year_from:
#                     movie_filters &= Q(release_date__year__gte=int(year_from))
#                     serie_filters &= Q(release_date__year__gte=int(year_from))
                
#                 if year_to:
#                     movie_filters &= Q(release_date__year__lte=int(year_to))
#                     serie_filters &= Q(release_date__year__lte=int(year_to))
                
#                 if min_rating:
#                     movie_filters &= Q(vote_average__gte=min_rating)
#                     serie_filters &= Q(vote_average__gte=min_rating)

#                 if max_rating:
#                     movie_filters &= Q(vote_average__lte=max_rating)
#                     serie_filters &= Q(vote_average__lte=max_rating)

#                 print("Still working until now") # debug print

#                 movies = Movie.objects.filter(title__icontains = search_query)
#                 series = Serie.objects.filter(title__icontains = search_query)

#                 print(f"Movie filters: {movie_filters}") # debug print
#                 print(f"Serie filters: {serie_filters}") # debug print

#                 movies = Movie.objects.filter(movie_filters)
#                 series = Serie.objects.filter(serie_filters)
                
#             print(f"\n movies: {movies}\n series: {series} ") # log print

#             total_found = movies.count() + series.count()
        

#             context = {
#                 'movies': movies,
#                 'series' : series,
#                 'query': search_query,
#                 'total_found': total_found,
#                 'year_from': year_from,
#                 'year_to': year_to,
#                 'min_rating': min_rating,
#                 'max_rating': max_rating,

#                 }
#             return render(request,'search/search.html', context=context)
        
        
#         except Exception as e:
#             context = {
#                 'error_message': f'An error occurred: {str(e)}',
#                 'query': search_query,
#             }
#             return render(request, 'search/search.html', context=context)

        