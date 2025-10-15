import django_filters
from django.db.models import Q
from django import forms

from movie.models import Movie
from serie.models import Serie

import datetime

class SharedMediaFilter(django_filters.FilterSet):
    '''Filter through both Movies and Series'''
    CONTENT_CHOICES = (
            ('all', 'All Content'),
            ('movie', 'Movies Only'),
            ('serie', 'Series Only'),
        )
    
    GENRE_CHOICES = (
        ('action', 'Action'), ('adventure', 'Adventure'),
        ('animation', 'Animation'),
        ('comedy', 'Comedy'), ('crime', 'Crime'),
        ('documentary', 'Documentary'), ('drama', 'Drama'),
        ('family', 'Family'), ('fantasy', 'Fantasy'),
        ('history', 'History'), ('horror', 'Horror'),
        ('music', 'Music'), ('mystery', 'Mystery'),
        ("news", "News"), ("reality", "Reality Show"),
        ('romance', 'Romance'), ('sci-fi', 'Sci-Fi'),
        ("soap", "Soap"), ("talk", "Talk"),
        ('thriller', 'Thriller'), ('tv movie', 'TV Movie'),
        ('war', 'War'), ('western', 'Western')
    )
# ('sport', 'Sport'),('superhero', 'Superhero'), ('short', 'Short'), 

    LANGUAGE_CHOICES = (
        ("da", 'Danish'), ("ar", 'Arabic'),
        ('bg', 'Bulgarian'), ('cs', 'Czech'),
        ('da', 'Danish'), ('de', 'German'),
        ('en', 'English'), ('fi', 'Finnish'),
        ('fr', 'French'), ('el', 'Greek'),
        ('nl', 'Dutch'), ('pl', 'Polish'),
        ('he', 'Hebrew'), ('hi', 'Hindi'),
        ('hu', 'Hungarian'), ('id', 'Indonesian'),
        ('it', 'Italian'), ('ja', 'Japanese'),
        ('no', 'Norwegian'), ('sv', 'Swedish'),
        ('pt', 'Portuguese'), ('es', 'Spanish'),
        ('ro', 'Romanian'), ('ru', 'Russian'),
        ('ko', 'Korean'), ('th', 'Thai'),
        ('tr', 'Turkish'), ('uk', 'Ukrainian'),
        ('vi', 'Vietnamese'), ('zh', 'Chinese')
    )

    curr_year = datetime.date.today().year


    language = django_filters.ChoiceFilter(
        choices=LANGUAGE_CHOICES,
        field_name='original_language',
        lookup_expr='exact',
        empty_label="select a language",   
        initial='all',
        label='Language',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select content type...',
            })
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
        method='filter_title',
        lookup_expr="icontains",
        label="Title",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title...',
        })
    )

    genre = django_filters.MultipleChoiceFilter(
        choices=GENRE_CHOICES,
        method='filter_genres', 
        label='Genre',
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'placeholder': 'Select a genre...',
            'style': 'height: 150px;',
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
            'min': '0',
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
            'max': '10',
            })
    )

    release_date = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year',
        label='Release Date',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type an exact year',
            'type': 'number',
            'min': '1900',  # set to start search from 1900
            'max': f'{curr_year}', # Max set to current year
            'style': 'width: 75%;',
            })
    )

    release_date_gte = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year__gte',
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'placeholder':'Starting range..',
            'type': 'number',
            'min': '1900',
            'style': 'width: 75%;',

            })
        )

    release_date_lte = django_filters.NumberFilter(
        method='check_release_date',
        lookup_expr='year__lte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder':'Ending range...',
            'type': 'number',
            'max': f'{curr_year}',
            'style': 'width: 75%;',
            })
        )
    
# ------- Ongoing work -------
#TODO:
# filter by length
# check if movies are less than 30min, 90min() or more than 120min, in between medium 
# find movies/series by the Cast/actors/directors/productions

    # Will include filter for casting, Also Director and Writer at the moment
    # casting = django_filters.CharFilter(
    #     field_name="casting__name",
    #     lookup_expr="icontains",
    #     label="Casting",
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Search by casting name...',
    #     })
    # )

# --------- End of ongoing work -------

    def check_release_date(self, queryset, name, value: int):
        """Custom filter method for release_date
        check if content_type is movie or serie
        and filter the queryset accordingly
        """
        # debug print below
        print(f"*Filtering by {name}: {value}")
        print(f"self.data is: {self.data}")
        print(f"self.data is: {queryset}")
        print(f"self.data.get('content_type') is: {self.data.get('content_type')}")
        print(f"queryset_model is: {queryset.model}\n")

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
                    print(f"value sci-fi changed to: '{genre}'\n.")

                filtered_queryset = filtered_queryset.filter(genre__icontains=genre)
            return filtered_queryset


    def filter_content_type(self, queryset, name, value):
        ''' This is a placeholder - actual filtering happens in the view '''
        return queryset

    # create a function to allow the title filter query to also check and return "original_title" if it is not found in the title field.
    def filter_title(self, queryset, name, value):
        """Custom filter method for title
        check if content_type is movie or serie
        and filter the queryset accordingly
        - 'name' is the name of the filter field being used
        - 'value' is the value passed in the filter field
        - 'queryset' contains all object instances of the queryset(or model being filtered: Movie or Serie)
        - 'queryset.model' is the model object being filtered 
        """
        print(f"Filtering by {name}: {value}")
        print(f"self.data is: {self.data}")
        print(f"queryset_model is: {queryset.model}")
        print(f"queryset is: {queryset}\n")
        try:
            # need to solve the issue only if title is used and with empty space
            # as it then returns all objects in the queryset!...

            value = value.strip()  # Remove leading/trailing whitespace
            if not value:  # If no search term provided
                return queryset

            title_query = Q(title__icontains=value) | Q(original_title__icontains=value)

            return queryset.filter(title_query).distinct()
        
        except Exception as e:
            print(f"Error filtering by title: {e}\n")


    class Meta:
        model = Movie  # Default model, will be overridden when creating filter instances in views.py
        fields = ['title', 'vote_average', 'genre', 'release_date', 'original_language']
