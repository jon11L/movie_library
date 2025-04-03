import django_filters

from movie.models import Movie
from serie.models import Serie

class MovieFilter(django_filters.FilterSet):
    # title = django_filters.CharFilter(lookup_expr='icontains')
    genre = django_filters.CharFilter(method='filter_genre', label='Genre')

    # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year', attrs={'class': 'form-control', 'placeholder':'Enter your first test test.'})
    # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')

    # rating = django_filters.NumberFilter()
    # rating__gt = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    # rating__lt = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Movie
        # fields = ['title', 'release_date', 'rating']


    # Alternative implementation for filtering // may not need the above implementation
        fields = {
            'title': ['icontains'], # , 'istartswith'
            'release_date': ['year', 'year__gte', 'year__lte'],
            'vote_average': ['exact', 'gte', 'lte'],
            'genre': ['exact'],
        }
        

    def filter_genre(self, queryset, name, value):
            """
            Custom filter method for JSONField 'genre'
            This will filter movies that have the specified genre in their genre list
            """
            
            return queryset.filter(genre__contains=[value])

# class MediaFilter(django_filters.FilterSet):
#     # title = django_filters.CharFilter(lookup_expr='icontains')

#     # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
#     # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
#     # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')

#     # rating = django_filters.NumberFilter()
#     # rating__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
#     # rating__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

#     class Meta:
#         model = Movie
#         # fields = ['title', 'release_date', 'rating']


#     # Alternative implementation for filtering // may not need the above implementation
#         fields = {
#             'title': ['icontains'], # , 'istartswith'
#             'release_date': ['year', 'year__gt', 'year__lt'],
#             'vote_average': ['exact', 'gte', 'lte'],
#         }



# class MediaFilter(django_filters.FilterSet):
#     # title = django_filters.CharFilter(lookup_expr='icontains')
#     # # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
#     # # vote_average = django_filters.NumberFilter(field_name='vote_average', lookup_expr='gte')
#     # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
#     # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
#     # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')
#     # rating = django_filters.NumberFilter()
#     # rating__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
#     # rating__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
#     #     # Alternative implementation for filtering // may not need the above implementation
#         fields = {
#             'title': ['icontains'],
#             'release_date': ['year', 'year__gt', 'year__lt'],
#             'vote_average': ['exact', 'gte', 'lte'],
#         }
#     # Common filter methods
    
# class MovieFilter(MediaFilter):
#     class Meta:
#         model = Movie
#         fields = ['title', 'release_date', 'vote_average']

# class SerieFilter(MediaFilter):
#     class Meta:
#         model = Serie
#         fields = ['title', 'Serie.Seasonrelease_date', 'vote_average']


