from django.db import models
# from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Movie(models.Model):

    class Rating(models.IntegerChoices):
        ONE = 1, '1 - Terrible'
        TWO = 2, '2 - Very Bad'
        THREE = 3, '3 - Bad'
        FOUR = 4, '4 - Poor'
        FIVE = 5, '5 - Average'
        SIX = 6, '6 - Fair'
        SEVEN = 7, '7 - Good'
        EIGHT = 8, '8 - Very Good'
        NINE = 9, '9 - Excellent'
        TEN = 10, '10 - Masterpiece'

    # External sources / for api references
    # tmdb_id = models.IntegerField(unique=True)  # Add this
    # imdb_id = models.CharField(max_length=20, blank=True, null=True)  # Add this
    # original_title = models.CharField(max_length=255, blank=True, null=True)  # Add this
    # vote_average = models.FloatField(blank=True, null=True)  # Add this for TMDB rating
    # vote_count = models.IntegerField(blank=True, null=True)  # Add this
    # popularity = models.FloatField(blank=True, null=True)  # Add this
    # backdrop_path = models.URLField(blank=True, null=True)  # Add this
    # imdb_rating = models.IntegerField(choices=Rating.choices, blank=True, null=True) 



    # Core Movie Details
    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    production = models.JSONField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    writer = models.JSONField(blank=True, null=True)
    casting = models.JSONField(blank=True, null=True)
    rating = models.IntegerField(choices=Rating.choices, blank=True, null=True) 
    length = models.IntegerField(blank=True, null=True) # will display the Movie time in minutes
    description = models.TextField(max_length=1000, blank=True, null=True)
    genre = models.JSONField(blank=True, null=True)  # This field an array of strings, i want 
    # budget = models.IntegerField(blank=True, null=True)
    image_poster = models.URLField(blank=True, null=True)
    # released = models.BooleanField(blank=True, null=True)

    # would serve to implement a check if a movie has a follow up, or part of a trilogy?
    # has_siblings = models.BooleanField(default=False)

    # Time stamp
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = 'movie'
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    
    def __str__(self):
        return self.title
    


    def render_genre(self):
        '''return the Movie.genre attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.genre:
            genre = ', '.join(self.genre)
            return genre
        else:
            return None
    
    
    def render_casting(self):
        '''return the Movie.casting attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.casting:
            casting = ', '.join(self.casting)
        return casting


    def render_writer(self):
        '''return the Movie.writer attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.writer:
            writer = ', '.join(self.writer)
        return writer