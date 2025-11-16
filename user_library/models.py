from django.db import models
from django.core.exceptions import ValidationError

from core.models import BaseModel
from user.models import User 
from movie.models import Movie
from serie.models import Serie


class WatchedContent(BaseModel):

    MOVIE = 'movie'
    SERIE = 'serie'

    CONTENT_TYPE_CHOICES = [
        (MOVIE, 'Movie'),
        (SERIE, 'Serie'),
    ]

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

    class RewatchChoice(models.TextChoices):
        NEVER = "never", "Never again."
        NO = "no", "Once was enough."
        MAYBE = "maybe", "Maybe in some years."
        WORTH = "worth", "It's Worth a rewatch."
        TOP = "totally", "Must rewatch it!"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched_content')
    content_type = models.CharField(max_length=25, choices=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    rating = models.IntegerField(choices=Rating.choices, blank=True, null=True)
    rewatch = models.CharField(choices=RewatchChoice.choices, blank=True, null=True)
    personal_note = models.TextField(max_length=2000, blank=True, null=True)


    class Meta:
        db_table = 'watched_content'
        verbose_name = 'watched_content'
        verbose_name_plural = 'watched_contents'
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.user.username} watched {self.content_type}: '{self.object_id}'"


class WatchList(BaseModel):


    class Status(models.TextChoices):
        PLANNED = 'to watch', 'Plan to Watch'
        WATCHING = 'watching', 'Currently Watching'
        FINISHED = 'finished', 'Finished Watching'
        DROPPED = 'dropped', 'Dropped out'


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='watchlist')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, null=True, blank=True, related_name='watchlist')
    personal_note = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(choices=Status.choices, blank=False, null=True)


    class Meta:
        db_table = 'watch_list'
        verbose_name = 'Watch_List'
        verbose_name_plural = 'Watch_Lists'
        ordering = ['-id']

        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(movie__isnull=False, serie__isnull=True) |
                    models.Q(movie__isnull=True, serie__isnull=False)
            ),
                name="only_one_content_type"
            ),
            models.UniqueConstraint(
                fields=['user', 'movie'],
                condition=models.Q(movie__isnull=False),
                name='unique_movie_watchlist'
            ),
            models.UniqueConstraint(
                fields=['user', 'serie'],
                condition=models.Q(serie__isnull=False),
                name='unique_serie_watchlist'
            ),
        ]
        unique_together = ('user', 'movie', 'serie')


    def __str__(self):
        object = self.movie or self.serie
        return f"{self.user.username} added {object}' to their watchlist"

    @property
    def kind(self) -> str:
        return 'movie' if self.movie != None else 'serie'

    @property
    def content_object(self):
        """Allow access to the movie or serie directly."""
        return self.movie or self.serie

    def clean(self):
        super().clean()
        if self.movie and self.serie:
            raise ValidationError("WatchList can only reference either a Movie or a Serie, not both.")
        if not self.movie and not self.serie:
            raise ValidationError("WatchList must reference either a Movie or a Serie.")

# --------------------------------------------------------------
    # def save(self, *args, **kwargs):
        # self.full_clean()
        # return super().save(*args, **kwargs)

# --------------------------------------------------------------

class Like(BaseModel):

    MOVIE = 'movie'
    SERIE = 'serie'

    CONTENT_TYPE_CHOICES = [
        (MOVIE, 'Movie'),
        (SERIE, 'Serie'),
    ]

    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE, related_name='liked')
    content_type = models.CharField(max_length=25, choices=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    # movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='like')
    # serie = models.ForeignKey(Serie, on_delete=models.CASCADE, null=True, blank=True, related_name='like')

    class Meta:
        db_table = "like"
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked {self.content_type} {self.object_id}"
