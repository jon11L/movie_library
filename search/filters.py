import django_filters
from django import forms

from movie.models import Movie
from serie.models import Serie

class SharedMediaFilter(django_filters.FilterSet):
    '''Filter through both Movies and Series'''
    CONTENT_CHOICES = (
            ('all', 'All Content'),
            ('movie', 'Movies Only'),
            ('serie', 'Series Only'),
        )
    
    GENRE_CHOICES = (
        ('Action', 'Action'),('adventure', 'Adventure'),('animation', 'Animation'),
        ('biography', 'Biography'),('comedy', 'Comedy'),('crime', 'Crime'),
        ('documentary', 'Documentary'),('family', 'Family'),('drama', 'Drama'),
        ('fantasy', 'Fantasy'),('history', 'History'),('horror', 'Horror'),
        ('music', 'Music'),('musical', 'Musical'),('mystery', 'Mystery'),
        ('romance', 'Romance'),('sci-fi', 'Sci-Fi'),('science fiction', 'Science Fiction'),
        ('short', 'Short'),('sport', 'Sport'),('superhero', 'Superhero'),
        ('thriller', 'Thriller'),('war', 'War'),('western', 'Western')
    )
# series has these gnere:
# ("Sci-Fi & Fantasy", "Sci-Fi & Fantasy"), ("Action & Adventure", "Action & Adventure"),
# ("soap", "Soap"), ("talk", "Talk"), ("reality", "Reality"),("kids", "Kids"),

    content_type = django_filters.ChoiceFilter(
        choices=CONTENT_CHOICES,
        empty_label=None,
        method='filter_content_type',
        initial='all',
        label='Content Type',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select content type...',
            })
    )

    title = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Title",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title...',
        })
    )

    # title = django_filters.CharFilter(lookup_expr='icontains')
    genre = django_filters.MultipleChoiceFilter(
        choices=GENRE_CHOICES,
        method='filter_genres', 
        label='Genre',
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'placeholder': 'Select a genre...',
            })
        )

    vote_average = django_filters.NumberFilter(
        # field_name="vote_average",
        lookup_expr="gte",
        label="Rating",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a rating here for an exact match',
            'type': 'number',
            })
    )

    release_date = django_filters.DateFromToRangeFilter(
        method='check_release_date',
        label='Release Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Select a date range...',
            })
    )

    def check_release_date(self, queryset, name, value):
        """Custom filter method for release_date
        check if content_type is movie or serie
        and filter the queryset accordingly
        """

        print(f"Filtering by release_date: {value}")
        print(f"type value: {type(value)}")
        if self.data.get('content_type') == 'movie':
            return queryset.filter(release_date__range=value)
        elif self.data.get('content_type') == 'serie':
            return queryset.filter(serie__first_air_date__range=value)
        else:
            return queryset.filter(release_date__range=value)
        

    # release_year = django_filters.NumberFilter(
    #     field_name='release_date', 
    #     lookup_expr='year', 
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control', 'placeholder':'Enter a year here for an exact match',
    #         'type': 'number',
    #         })
    #     )
    
    # release_year__gt = django_filters.NumberFilter(
    #     field_name='release_date', 
    #     lookup_expr='year__gte',
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control', 'placeholder':'Enter a year for a begin range',
    #         'type': 'number',
    #         })
    #     )
    



    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')

    # rating = django_filters.NumberFilter()
    # rating__gt = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    # rating__lt = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')


    # Alternative implementation for filtering // may not need the above implementation
        # fields = {
        #     # 'title': ['icontains'], # , 'istartswith'
        #     # 'release_date': ['year', 'year__gte', 'year__lte'],
        #     # 'vote_average': ['exact', 'gte', 'lte'],
        #     # 'genre': ['exact'],
        # }
        

    def filter_genres(self, queryset, name, value):
            """
            Custom filter method for JSONField 'genre'
            This will filter movies that have the specified genre in their genre list
            """
            print(f"Filtering by genre: {value}")
            print(f"type value: {type(value)}")

            # for genre in value:
            #     print(f"Genre: {genre}")
            #     if genre is

            # check if the selected value is in the genre list of the movie
            return queryset.filter(genre__name__icontains=[value])

    

    def filter_content_type(self, queryset, name, value):
        ''' This is a placeholder - actual filtering happens in the view '''
        return queryset



    class Meta:
        # This meta class is required, but we'll override it in each instance
        model = Movie  # Default model, will be overridden when creating filter instances
        fields = ['title', 'vote_average', 'genre']



# class MovieFilter(SharedMediaFilter):
#     class Meta:
#         model = Movie
#         fields = ['title', 'vote_average']

# class SerieFilter(SharedMediaFilter):
#     class Meta:
#         model = Serie
#         fields = ['title', 'vote_average']


