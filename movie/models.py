from django.db import models

class Movie(models.Model):

    # External sources / for api references
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    imdb_id = models.CharField(max_length=20, blank=True, null=True) # same as above
    original_title = models.CharField(max_length=255, blank=True, null=True)

    # Metrics
    vote_average = models.FloatField(blank=True, null=True)  # for TMDB rating
    vote_count = models.IntegerField(blank=True, null=True)  
    imdb_rating = models.FloatField(blank=True, null=True)  
    popularity = models.FloatField(blank=True, null=True)  


    # Core Movie Details
    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    production = models.JSONField(blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    writer = models.JSONField(blank=True, null=True)
    casting = models.JSONField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True) # will display the Movie time in minutes
    description = models.TextField(max_length=1000, blank=True, null=True)
    genre = models.JSONField(blank=True, null=True)  # This field an array of strings, i want 
    budget = models.IntegerField(blank=True, null=True)
    revenue = models.BigIntegerField(blank=True, null=True)  # Movie's box office revenue
    image_poster = models.URLField(blank=True, null=True) # vertical poster ( made for list,dvd format..)

    banner_poster = models.URLField(blank=True, null=True) # banner image ( wide format)
    released = models.BooleanField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)  # Movie's tagline/slogan

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