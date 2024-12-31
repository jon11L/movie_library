from django.db import models

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

    # Core Movie Details
    title = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    production = models.CharField(max_length=255, blank=True, null=True)
    casting = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(choices=Rating.choices, blank=True, null=True) 
    description = models.TextField(blank=True, null=True)
    genre = models.TextField(blank=True, null=True)  # This field type is a guess.

    # Time stamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # film_poster = models.ImageField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie'

    
    def __str__(self):
        return self.title