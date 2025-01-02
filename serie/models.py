from django.db import models

# Create your models here.
class Serie(models.Model):

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

    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    production = models.CharField(max_length=255, blank=True, null=True)
    casting = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(choices=Rating.choices, blank=True, null=True)  # This field type is a guess.
    description = models.TextField(blank=True, null=True)
    ongoing = models.BooleanField(blank=True, null=True)
    serie_poster = models.URLField(blank=True, null=True)
    # length = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'serie'
        verbose_name = 'Serie'
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title



class Season(models.Model):
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.PositiveSmallIntegerField(blank=True, null=True)
    episode = models.PositiveSmallIntegerField(blank=True, null=True)


    class Meta:
        db_table = 'season'
        unique_together = ('serie', 'season_number')
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'

    
    def __str__(self):
        return f"{self.serie.title} - Season {self.season_number}"
    


class Episode(models.Model):

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveSmallIntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    casting = models.TextField(blank=True, null=True)


    class Meta:

        db_table = 'episode'
        unique_together = ('season', 'episode_number')
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'


    def __str__(self):
        return f"{self.season} - Episode {self.episode_number}: {self.title}"