from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Serie(models.Model):

    # External unique identifier / sources for api references
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)  # allow to find the content id in TMDB
    imdb_id = models.CharField(max_length=20, blank=True, null=True) # same as above

    # core details
    original_title = models.CharField(max_length=255, blank=True, null=True) # if title not english get from: ["original_name"]
    title = models.CharField(max_length=255) # ["name"]
    description = models.TextField(blank=True, null=True)
    genre = models.JSONField(blank=True, null=True)
    origin_country = models.JSONField(blank=True, null=True) # ["origin_country", []]
    original_language = models.CharField(max_length=50, blank=True, null=True)  # Movie's original language
    spoken_languages = models.JSONField(blank=True, null=True) # take from the list of dict: ['spoken_languages', []] "english_name"
    tagline = models.TextField(blank=True, null=True) # ["tagline"]
    # Cast and Prod
    production = models.JSONField(blank=True, null=True) # ["production_companies"]
    created_by = models.JSONField(blank=True, null=True) # ["created_by"]
    first_air_date = models.DateField(blank=True, null=True) # ["first_air_date"]
    last_air_date = models.DateField(blank=True, null=True) # ["last_air_date"]
    # casting = models.JSONField(blank=True, null=True) # ["credits", {}] ['cast', []] as main actors  ---/ guest stars [""guest_stars""] loop through 8 or so.... make a list of dict with key, main and guest star (inside each names and roles)

    # Metrics
    vote_average = models.FloatField(blank=True, null=True)  # for TMDB rating
    vote_count = models.IntegerField(blank=True, null=True)
    # images
    image_poster = models.URLField(blank=True, null=True) # ["poster_path"]
    banner_poster = models.URLField(blank=True, null=True) # ["backdrop_path"]
    status = models.CharField(blank=True, null=True) # use ["in_production"]: to check if true or false, // or with ["status"]

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
    
    def render_vote_average(self):
        '''return the Movie.vote_average with a rounded number'''
        if self.vote_average:
            return round(self.vote_average, 1)
        else:
            return 0

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
    
    def render_average_time(self):
        '''return the Serie' length in average per episode time
        '''
        average_length = self.seasons.episodes.aggregate(models.Avg('episodes__length'))['episodes__length__avg']


class Season(models.Model):

    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name='seasons') 
    name = models.CharField(max_length=255, blank=True, null=True)
    season_number = models.IntegerField(blank=True, null=True)
    producer = models.JSONField(max_length=255, blank=True, null=True)
    casting = models.JSONField(blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 
    image_poster = models.URLField(blank=True, null=True) 
    trailers = models.JSONField(max_length=11, blank=True, null=True) 
    # external sources ID
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
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
        return f"season: {self.season_number} - {self.name}"

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


class Episode(models.Model):

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
    banner_poster = models.URLField(blank=True, null=True) # ["still_path"]
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
    