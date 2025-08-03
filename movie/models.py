from django.db import models
from core.models import BaseModel

class Movie(BaseModel):

    # External unique identifier / sources for api references
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    imdb_id = models.CharField(max_length=20, blank=True, null=True) # same as above

    # Core Movie Details
    original_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    origin_country = models.JSONField(blank=True, null=True)
    original_language = models.CharField(max_length=50, blank=True, null=True)  # Movie's original language
    spoken_languages = models.JSONField(blank=True, null=True) # take from the list of dict: ['spokent_languages'] "english_name"
    description = models.TextField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True) # will display the Movie time in minutes
    genre = models.JSONField(blank=True, null=True)  # This field will be a list of strings
    tagline = models.TextField(blank=True, null=True)  # Movie's tagline/slogan
    released = models.BooleanField(blank=True, null=True)
    # Cast and Prod
    production = models.JSONField(blank=True, null=True)
    director = models.JSONField(blank=True, null=True)
    writer = models.JSONField(blank=True, null=True)
    casting = models.JSONField(blank=True, null=True)
    
    budget = models.IntegerField(blank=True, null=True)
    revenue = models.BigIntegerField(blank=True, null=True)  # Movie's box office revenue
    # Metrics
    vote_average = models.FloatField(blank=True, null=True)  # for TMDB rating
    vote_count = models.IntegerField(blank=True, null=True)  
    imdb_rating = models.FloatField(blank=True, null=True)  # to fetch externally their rating
    popularity = models.FloatField(blank=True, null=True)  
    # images
    image_poster = models.URLField(blank=True, null=True) # vertical poster ( made for list,dvd format..)
    banner_poster = models.URLField(blank=True, null=True) # banner image ( wide format)
    # trailers
    trailers = models.JSONField(max_length=11, blank=True, null=True)
    # would serve to implement a check if a movie has a follow up, or part of a trilogy?
    # has_siblings = models.BooleanField(default=False)


    class Meta:
        db_table = 'movie'
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
        ordering = ['id']

    def __str__(self):
        return self.title

    # The below functions are to format the fields for a better human readable display.
    def render_genre(self):
        '''return the Movie.genre attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.genre:
            genre = ', '.join(self.genre)
            return genre
        return 'N/a'

    def render_casting(self):
        '''return the Movie.casting attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.casting:
            casting = ', '.join([f"{cast['name']} as {cast['role']}" for cast in self.casting])
            return casting
        return 'N/a'

    def render_writer(self):
        '''return the Movie.writer attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.writer:
            writer = ', '.join(self.writer)
            return writer
        return 'N/a'

    def render_production(self):
        '''return the Movie.production attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.production:
            production = ', '.join(self.production)
            return production 
        return 'N/a'   

    def render_director(self):
        '''return the Movie.director attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.director:
            director = ', '.join(self.director)
            return director
        return 'N/a'

    def render_vote_average(self):
        '''return the Movie.vote_average with a rounded number'''
        if self.vote_average:
            return round(self.vote_average, 1)
        else:
            return 0
        
    def render_origin_country(self):
        '''return the Movie.origin_country with a comma-separated string'''
        if self.origin_country:
            origin_country = ', '.join(self.origin_country)
            return origin_country  
        return 'N/a' 
    
    def render_length(self):
        '''return the Movie.length with a formatted string
        (e.g., 1h 30m)
        '''
        if self.length:
            minutes = self.length % 60
            hours = self.length // 60
            if hours == 0:
                return f'{minutes}min'
            
            elif hours > 0 and minutes <= 9:
                return f'{hours}h0{minutes}'
            else:
                return f'{hours}h{minutes}'
        return 'N/a'
    

    def render_trailer(self):
        ''' concatenates the field "trailers" to a base url'''
        if self.trailers:
            trailer_link = f'https://www.youtube.com/watch?v={self.trailers}'
            return trailer_link
        return 'Trailers Not found'
    

    def render_spoken_languages(self):
        ''' return the Movie.spoken_languages with a comma-separated string'''
        if self.spoken_languages:
            spoken_languages = ', '.join(self.spoken_languages)
            return spoken_languages
        return 'N/a'

    def render_banner_poster(self):
        ''' return the Movie.banner_poster with a formatted string'''
        if self.banner_poster:
            banner_poster = f"https://image.tmdb.org/t/p/w1280{self.banner_poster}" # for a width1280
            return banner_poster
        return None

    def render_image_poster(self):
        ''' return the Movie.banner_poster with a formatted string'''
        if self.image_poster:
            image_poster = f"https://image.tmdb.org/t/p/w500{self.image_poster}" # for a width500
            return image_poster
        return None

    def render_release_date(self):
        '''return the Episode.release_date with a formatted string'''
        if self.release_date:
            release_date = self.release_date.strftime("%b. %d, %Y")
            return release_date
        return 'N/a'
    