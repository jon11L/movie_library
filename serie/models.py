from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from core.models import BaseModel

import random
from django.templatetags.static import static

class Serie(BaseModel):

    # External unique identifier / sources for api references
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    imdb_id = models.CharField(max_length=20, blank=True, null=True) # same as above

    # core details
    original_title = models.CharField(max_length=255, blank=True, null=True) # if title not english get from: ["original_name"]
    title = models.CharField(max_length=255) # ["name"]
    description = models.TextField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True) # ["tagline"]
    genre = models.JSONField(blank=True, null=True)
    first_air_date = models.DateField(blank=True, null=True) # ["first_air_date"]
    last_air_date = models.DateField(blank=True, null=True) # ["last_air_date"]
    origin_country = models.JSONField(blank=True, null=True) # ["origin_country", []]
    original_language = models.CharField(max_length=50, blank=True, null=True)  # languages
    spoken_languages = models.JSONField(blank=True, null=True) # take from the list of dict: ['spoken_languages', []] "english_name"
    # Cast and Prod
    production = models.JSONField(blank=True, null=True) # ["production_companies"]
    created_by = models.JSONField(blank=True, null=True) # ["created_by"]
    # casting = models.JSONField(blank=True, null=True) # ["credits", {}] ['cast', []] as main actors  ---/ guest stars [""guest_stars""] loop through 8 or so.... make a list of dict with key, main and guest star (inside each names and roles)

    # Metrics
    vote_average = models.FloatField(blank=True, null=True)  # for TMDB rating
    vote_count = models.IntegerField(blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)  # for TMDB popularity
    # images
    poster_images = ArrayField(
        models.CharField(max_length=255), default=list, blank=True
    ) # ['images].get("posters")

    banner_images = ArrayField(
        models.CharField(max_length=255), default=list, blank=True
    ) # ['images].get("backdrops")

    status = models.CharField(max_length=255, blank=True, null=True) # use ["in_production"]: to check if true or false, // or with ["status"]

    class Meta:
        db_table = 'serie'
        verbose_name = 'Serie'
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title
    

    def render_genre(self):
        '''return the Serie.genre attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.genre:
            genre = ' - '.join(self.genre)
            return genre
        else:
            return None
        
    def render_production(self):
        '''return the serie.production attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.production:
            production = ', '.join(self.production)
            return production 
        return 'N/a' 

    def render_created_by(self):
        '''return the Serie.production attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.created_by:
            created_by = ', '.join(self.created_by)
            return created_by 
        return 'N/a' 

    def render_origin_country(self):
        '''return the Serie.origin_country with a comma-separated string'''
        if self.origin_country:
            origin_country = ', '.join(self.origin_country)
            return origin_country  
        return 'N/a'
    
    def render_spoken_languages(self):
        '''return the Serie.spoken_languages with a comma-separated string'''
        if self.spoken_languages:
            spoken_languages = ', '.join(self.spoken_languages)
            return spoken_languages  
        return 'N/a'
    
    def render_vote_average(self):
        '''return the Movie.vote_average with a rounded number'''
        if self.vote_average:
            return round(self.vote_average, 1)
        else:
            return 0

    def render_banner(self):
        '''
        return the Movie.banner_poster with a formatted string
        Fallback to a default image if no banners are available

        '''
        if self.banner_images:
            if len(self.banner_images) >= 2:
                num = random.randint(0, len(self.banner_images) -1)
                banner = f"https://image.tmdb.org/t/p/w1280{self.banner_images[num]}" # for a width1280
            else:
                banner = f"https://image.tmdb.org/t/p/w1280{self.banner_images[0]}" # for a width1280
            return banner
        return static("images/default_banner_photo.jpg")

    def render_poster(self):
        '''
        return the Movie.banner_poster with a formatted string
        Fallback to a default image if no posters are available
        '''
        if self.poster_images:
            poster = f"https://image.tmdb.org/t/p/w500{self.poster_images[0]}" # for a width500
            return poster
        return static("images/default_poster_photo.jpg")
    
    def render_first_air_date(self):
        '''return the Episode.release_date with a formatted string'''
        if self.first_air_date:
            first_air_date = self.first_air_date.strftime("%b. %d, %Y")
            return first_air_date
        return 'N/a'
    
    # def render_average_time(self):
    #     '''return the Serie' length in average per episode time
    #     '''
        # pass

class Season(BaseModel):

    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name='seasons') 
    name = models.CharField(max_length=255, blank=True, null=True)
    season_number = models.IntegerField(blank=True, null=True)
    producer = models.JSONField(max_length=255, blank=True, null=True)
    casting = models.JSONField(blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 

    poster_images = ArrayField(
        models.CharField(max_length=255), default=list, blank=True
    )  # ['images].get("posters")

    trailers = models.JSONField(max_length=11, blank=True, null=True) 
    # external sources ID
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        db_table = 'season'
        unique_together = ('serie', 'season_number')
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        ordering = ['serie', 'season_number']


    def __str__(self):
        if f"Season {str(self.season_number)}" == self.name:
            return f"{self.name}"
        else:
            return f"Season: {self.season_number} - {self.name}"

    def render_casting(self):
        '''return the Movie.casting attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.casting:
            casting = ', '.join(self.casting)
            return casting
        return 'N/a'

    def render_trailer(self):
        ''' concatenates the field "trailers" to a base url'''
        if self.trailers:
            trailer_link = f'https://www.youtube.com/watch?v={self.trailers}'
            return trailer_link
        return 'Trailer Not found'

    def render_poster(self):
        ''' return the Movie.banner_poster with a formatted string'''
        if self.poster_images:
            poster = f"https://image.tmdb.org/t/p/w500{self.poster_images[0]}" # for a width500
            return poster
        return None
    


class Episode(BaseModel):

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveSmallIntegerField(blank=True, null=True)# loop through ["episodes"] first then: ["episode_number"]
    title = models.CharField(max_length=255, blank=True, null=True) # ["name"]
    description = models.TextField(blank=True, null=True) # ["overview"]
    length = models.IntegerField(
        help_text="Average episode length in minutes",
        validators=[MinValueValidator(1)],
        blank=True, null=True
        ) # ["runtime"]

    release_date = models.DateField(blank=True, null=True) # [""air_date""]
    guest_star = models.JSONField(blank=True, null=True) # ["credits", {}] ["guest_stars", {}] 
    director = models.JSONField(blank=True, null=True)
    writer = models.JSONField(blank=True, null=True) # when ['job'] = Writer
    # image

    banner_images = ArrayField(
        models.CharField(max_length=255), default=list, blank=True
    ) # ['images].get("stills")

    # external sources ID
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB

    class Meta:

        db_table = 'episode'
        unique_together = ('season', 'episode_number')
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'
        ordering = ['season', 'episode_number']


    def __str__(self):
        return f"{self.episode_number} - {self.title}"
    

    def render_length(self):
        '''return the episode length with a formatted string
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
    

    def render_director(self):
        '''return the Movie.director attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.director:
            director = ', '.join(self.director)
            return director
        return 'N/a'


    def render_writer(self):
        '''return the Movie.wrtier attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.writer:
            writer = ', '.join(self.writer)
            return writer
        return 'N/a'
    
    def render_release_date(self):
        '''return the Episode.release_date with a formatted string'''
        if self.release_date:
            release_date = self.release_date.strftime("%b. %d, %Y")
            return release_date
        return 'N/a'