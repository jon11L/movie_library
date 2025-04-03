from django.shortcuts import render
# from django.db.models import Q
from .filters import MovieFilter
# from .filters import MediaFilter
# from .filters import SerieFilter
from movie.models import Movie
from serie.models import Serie
from user_library.models import Like

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

    # Check if any filter parameters have values
    has_filter_values = False
    for key, value in request.GET.items():
        if value and key not in ['page', 'csrfmiddlewaretoken']:
            has_filter_values = True
            break
    
    print(f"has_filter_values: {has_filter_values}")  # Debug print
    
    # Default to empty queryset if no filters applied
    base_queryset = Movie.objects.all() if has_filter_values else Movie.objects.none()

    movie_filters = MovieFilter(request.GET, queryset=base_queryset)
    
    # Initial search page load, user reach the search page without any query/filter/request
    if request.method == 'GET' and not request.GET:
        print("going to search page") # debug print

        context ={
            'filter': movie_filters,
            # 'filtered_movies': movie_filters.qs
        }

        return render(request, 'search/search.html', context=context)

    # Handle GET requests with parameters
    # if request.method == 'GET' and request.GET:
    if request.method == 'GET':
        # return no movies when no filter is selected

        if not has_filter_values:
            context = {
                'filter': movie_filters,
                # 'filtered_movies': movie_filters.qs,  # This will be empty
                'no_filters_applied': True  # Flag to show a message in the template
            }
        
        else:
            filtered_movies = movie_filters.qs
            total_found = filtered_movies.count()
            print("should have parameters value") # debug print

            # Get the user's liked content (movies, series)
            user_liked_movies = []
            user_liked_movies = Like.objects.filter(
                                                user=request.user.id, content_type='movie'
                                                ).values_list('object_id', flat=True)

            user_liked_series = []
            user_liked_series = Like.objects.filter(
                                                user=request.user.id, content_type='serie'
                                                ).values_list('object_id', flat=True)

            context = {
                'filter': movie_filters,
                'filtered_movies': filtered_movies,
                'total_found': total_found,
                'user_liked_movies': user_liked_movies,
                'user_liked_series': user_liked_series
            }

        return render(request, 'search/search.html', context=context)


    # Handle the search bar submission query
    if request.method == 'POST':
        # Get the search query from the form input and filter movies and series by the query.
        search_query = request.POST.get('search_query', "").lower()

        # serie_filter = SerieFilter(request.GET, queryset=Serie.objects.all())
        # Search through media content: movies, series
        try:
            if search_query:
            # filtered_movies = movie_filters.qs
                movies = Movie.objects.filter(title__icontains=search_query)
                series = Serie.objects.filter(title__icontains=search_query)

            # Get the user's liked content (movies, series)
            user_liked_movies = []
            user_liked_movies = Like.objects.filter(
                                                user=request.user.id, content_type='movie'
                                                ).values_list('object_id', flat=True)

            user_liked_series = []
            user_liked_series = Like.objects.filter(
                                                user=request.user.id, content_type='serie'
                                                ).values_list('object_id', flat=True)

            # print("Working until now") # debug print

            # print(f"Movie filters: {filtered_movies}") # debug print
            # print(f"Serie filters: {serie_filters}") # debug print
            print(f"\n movies: {movies}\n series: {series} ") # log print

            total_found = movies.count() + series.count()
            print(f"Total found: {total_found}")

            context = {
                'movies': movies,
                'series' : series,
                'query': search_query,
                'total_found': total_found,
                'no_filters_applied': True,  # Flag to show a message in the template
                'filter': movie_filters,
                'user_liked_movies': user_liked_movies,
                'user_liked_series': user_liked_series
                # 'filtered_movies': filtered_movies
                }
            return render(request,'search/search.html', context=context)
        
        except Exception as e:
            context = {
                'error_message': f'An error occurred: {str(e)}',
                'query': search_query,
            }
            return render(request, 'search/search.html', context=context)



    # if request.method == 'GET' and not has_filter_params:
    # # Initial page load or filter form submitted with no criteria
    #     print("No movies found, walalala")
    #     context = {
    #         'filter': movie_filters,
    #         'filtered_movies': movie_filters.qs,  # This will be empty
    #         'no_filters_applied': True  # Flag to show a message in the template
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

        