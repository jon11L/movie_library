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
        ('Action', 'Action'), ('adventure', 'Adventure'), ('animation', 'Animation'),
        ('biography', 'Biography'), ('comedy', 'Comedy'), ('crime', 'Crime'),
        ('documentary', 'Documentary'), ('drama', 'Drama'), ('family', 'Family'),
        ('fantasy', 'Fantasy'), ('history', 'History'), ('horror', 'Horror'),
        ('music', 'Music'), ('musical', 'Musical'), ('mystery', 'Mystery'),
        ("reality", "Reality"), ('romance', 'Romance'), ('sci-fi', 'Sci-Fi'),
        ('short', 'Short'), ("soap", "Soap"), ('sport', 'Sport'), ('superhero', 'Superhero'),
        ("talk", "Talk"), ('thriller', 'Thriller'), ('war', 'War'), ('western', 'Western')
    )

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

    # vote_average = django_filters.NumberFilter(
    #     field_name="vote_average",
    #     lookup_expr="",
    #     label="Rating",
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Enter an exact rating score',
    #         'type': 'number',
    #         })
    # )

    vote_average_gte = django_filters.NumberFilter(
        field_name="vote_average",
        lookup_expr="gte",
        label="Rating",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rating from..  eg: 2',
            'type': 'number',
            })
    )

    vote_average_lte = django_filters.NumberFilter(
        field_name="vote_average",
        lookup_expr="lte",
        label="Rating",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rating to..  eg: 7.5',
            'type': 'number',
            })
    )




    release_date = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year',
        label='Release Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type in an exact year',
            })
    )

    release_date_gte = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year__gte',
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'placeholder':'Enter a starting range..',
            'type': 'number',
            })
        )
    
    release_date_lte = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year__lte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder':'Enter a ending range...',
            'type': 'number',
            })
        )
    

# filter by length
# check if movies are less than 30min, 90min() or more than 120min, in between medium 


    def check_release_date(self, queryset, name, value: int):
        """Custom filter method for release_date
        check if content_type is movie or serie
        and filter the queryset accordingly
        """
        # debug print
        print(f"*Filtering by {name}: {value}")
        print(f"self.data is: {self.data}")
        print(f"self.data is: {queryset}")
        print(f"self.data.get('content_type') is: {self.data.get('content_type')}")
        print(f"queryset_model is: {queryset.model}")

        # if 'release_date_lte' in self.data:
        #     print(f"data rel.date.gte found..------")

        if hasattr(queryset.model, 'release_date'):
            if 'gte' in name:
                return queryset.filter(release_date__year__gte=value)
            elif 'lte' in name:
                return queryset.filter(release_date__year__lte=value)
            else:
                return queryset.filter(release_date__year=value)
        elif hasattr(queryset.model, 'first_air_date'):
            if 'gte' in name:
                return queryset.filter(first_air_date__year__gte=value)
            elif 'lte' in name:
                return queryset.filter(first_air_date__year__lte=value)
            else:
                return queryset.filter(first_air_date__year=value)



    def filter_genres(self, queryset, name, value):
            """
            Custom filter method for JSONField 'genre'
            This will filter content that have the specified genre in their genre list
            """
            print(f"Filtering by genre: {value}")

            print(f"query_set: {queryset} ")
            filtered_queryset = queryset
            print(f"content_type is:  {self.data.get('content_type')}")
            
            # For each selected genre, filter the queryset
            # to include only those that contain the genre in their genre list
            print(f"queryset_model: {queryset.model}")

            for genre in value:
                print(f"Filtering for genre: {genre}")
                # check content_type Movie or Serie , and change Sci-Fi to Science Fiction if model is Movie
                if genre == "sci-fi" and queryset.model.__name__ == "Movie":
                    genre = "science fiction"
                    print(f"value sci-fi changed to: '{genre}'.")

                filtered_queryset = filtered_queryset.filter(genre__icontains=genre)
            return filtered_queryset


    def filter_content_type(self, queryset, name, value):
        ''' This is a placeholder - actual filtering happens in the view '''
        return queryset


    class Meta:
        # This meta class is required, but we'll override it in each instance
        model = Movie  # Default model, will be overridden when creating filter instances
        fields = ['title', 'vote_average', 'genre', 'release_date']



