from django.db import models

# Create your models here.
from core.models import BaseModel
from user.models import User 
from media_library.models import Media

class WatchList(BaseModel):

    class Status(models.TextChoices):
        PLANNED = 'to watch', 'Plan to Watch'
        WATCHING = 'watching', 'Currently Watching'
        FINISHED = 'finished', 'Finished Watching'
        DROPPED = 'dropped', 'Dropped out'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    media = models.ForeignKey(
        Media, on_delete=models.CASCADE, related_name="watchlisted_by"
    )

    personal_note = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(
        choices=Status.choices, max_length=128, default=None, blank=True, null=True
    )

    class Meta:
        db_table = 'watchlist'
        verbose_name = 'Watchlist'
        verbose_name_plural = 'Watchlists'
        ordering = ['-id']
        unique_together = ('user', 'media')

    def __str__(self):
        return f"{self.media} -- ({self.status}) "

    # @property
    # def media(self):
    #     """Allow access to the movie or serie directly."""
    #     # return self.movie or self.serie
    #     return self.media

    # def clean(self):
    #     super().clean()
    #     if self.movie and self.serie:
    #         raise ValidationError("WatchList can only reference either a Movie or a Serie, not both.")
    #     if not self.movie and not self.serie:
    #         raise ValidationError("WatchList must reference 1 model, either Movie or Serie.")

# --------------------------------------------------------------
# def save(self, *args, **kwargs):
# self.full_clean()
# return super().save(*args, **kwargs)
