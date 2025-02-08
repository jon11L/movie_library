from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Serie(models.Model):

    # core details
    original_title = models.CharField(max_length=255, blank=True, null=True) # if title not english get from: ["original_name"]
    title = models.CharField(max_length=255) # ["name"]
    origin_country = models.JSONField(blank=True, null=True) # ["origin_country", []]
    original_language = models.CharField(max_length=50, blank=True, null=True)  # Movie's original language
    spoken_languages = models.JSONField(blank=True, null=True) # take from the list of dict: ['spokent_languages', []] "english_name"
    description = models.TextField(blank=True, null=True)
    genre = models.JSONField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True) # ["tagline"]
    # Cast and Prod
    production = models.JSONField(blank=True, null=True) # ["production_companies"]
    created_by = models.CharField(blank=True, null=True) # ["created_by"]
    # Metrics
    vote_average = models.FloatField(blank=True, null=True)  # for TMDB rating
    vote_count = models.IntegerField(blank=True, null=True)
    # images
    image_poster = models.URLField(blank=True, null=True) # ["poster_path"]
    banner_poster = models.URLField(blank=True, null=True) # ["backdrop_path"]
    ongoing = models.BooleanField(blank=True, null=True) # use ["in_production"]: to check if true or false, // or with ["status"]
    # External unique identifier / sources for api references
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    # Time stamp
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'serie'
        verbose_name = 'Serie'
        verbose_name_plural = 'Series'

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
        
    def render_production(self):
        '''return the Movie.production attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.production:
            production = ', '.join(self.production)
            return production 
        return 'N/a' 

    def render_origin_country(self):
        '''return the Movie.origin_country with a comma-separated string'''
        if self.origin_country:
            origin_country = ', '.join(self.origin_country)
            return origin_country  
        return 'N/a' 


# ["seasons"] will return a list of dictionnary with the seasons id in it ["i"]

class Season(models.Model):

    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name='seasons') # ["season_number"]

    season_number = models.PositiveSmallIntegerField(blank=True, null=True)
    # Crew and staff
    director = models.CharField(max_length=255, blank=True, null=True) # when ['job'] = Director
    writer = models.JSONField(blank=True, null=True) # when ['job'] = Writer
    casting = models.JSONField(blank=True, null=True) # ["credits", {}] ['cast', []] as main actors  ---/ guest stars [""guest_stars""] loop through 8 or so.... make a list of dict with key, main and guest star (inside each names and roles)

    description = models.TextField(max_length=1000, blank=True, null=True) # ["overview"]
    image_poster = models.URLField(blank=True) # ["still_path"]

    trailers = models.JSONField(max_length=11, blank=True, null=True) # ["videos", {}] ["results", []]

    # external sources ID
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    imdb_id = models.CharField(max_length=20, blank=True, null=True) # same as above

    # Time stamp
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'season'
        unique_together = ('serie', 'season_number')
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        ordering = ['serie', 'season_number']


    def __str__(self):
        return f"{self.season_number}"

    def render_casting(self):
        '''return the Movie.casting attribute in without quotes and [],
        only comma-separated string.
        '''
        if self.casting:
            casting = ', '.join(self.casting)
            return casting
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
    

    def render_trailer(self):
        ''' concatenates the field "trailers" to a base url'''
        if self.trailers:
            trailer_link = f'https://www.youtube.com/watch?v={self.trailers}'
            return trailer_link
        return 'Trailer Not found'


class Episode(models.Model):

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='episodes'
        )

    episode_number = models.PositiveSmallIntegerField(blank=True, null=True) # ["episode_number"]
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    length = models.IntegerField(
        help_text="Average episode length in minutes",
        validators=[MinValueValidator(1)],
        blank=True, null=True
        )

    release_date = models.DateField(blank=True, null=True) # [""air_date""]

    # external sources ID
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB

    # Time stamp
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        db_table = 'episode'
        unique_together = ('season', 'episode_number')
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'
        ordering = ['season', 'episode_number']


    def __str__(self):
        return f"{self.episode_number} - {self.title}"
    

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