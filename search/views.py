from django.shortcuts import render

from movie.models import Movie
from serie.models import Serie

# Create your views here.
def search(request):
    """
    View function for search page
    """

    if request.method == 'GET':
        return render(request, 'search/search.html', {})
    
    if request.method == 'POST':
        # Get the search query from the form input and filter movies and series by the query.
        search_query = ""
        search_query = request.POST.get('search_query').lower()

        movies = []
        series = []
        print(f"\nsearch query given: {search_query} ")

        # Search through media content: movies, series
        try:
            if search_query:
                movies = Movie.objects.filter(title__icontains = search_query)
                series = Serie.objects.filter(title__icontains = search_query)
                
            print(f"\n movies: {movies}\n\n series: {series} ")

            total_found = movies.count() + series.count()
        
            context = {
                'movies': movies,
                'series' : series,
                'query': search_query,
                'total_found': total_found,
                }
            return render(request,'search/search.html', context=context)
        
        except Movie.DoesNotExist:
            print("no movie found")



