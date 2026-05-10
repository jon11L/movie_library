from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import BaseModel
from media_library.models import Media
# from user.models import User
# Create your models here.

class Review(BaseModel):

    """Records that a user has watched or is watching a piece of media."""
    STATUS_WATCHING = 'watching'
    STATUS_COMPLETED = 'completed'
    STATUS_DROPPED = 'dropped'
    STATUS_PAUSED = 'paused'

    STATUS_CHOICES = [
        (STATUS_WATCHING, 'Watching'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DROPPED, 'Dropped'),
        (STATUS_PAUSED, 'Paused'),
    ]

    class RewatchChoice(models.TextChoices):
        '''Would you personally recommend or rewatch this media.'''
        NO = "no", "Once was enough."
        MAYBE = "maybe", "Maybe."
        YES = "yes", "Yes, worth it."


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
    )
    review = models.TextField(max_length=2000, blank=True, null=True)
    rewatch = models.CharField(choices=RewatchChoice.choices, max_length=20, blank=True, null=True)

    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Score between 0.0 and 10.0",
        null=True,
        blank=True
    )


    class Meta:
        db_table = "review"
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'media'],
                name='unique_user_media_watched'
            )
        ]

    def __str__(self):
        return f"{self.user.username}: {self.media} -({self.status}) - '{self.score}/10'"


    # @classmethod
    # def completed_count(cls, user, media_type=None):
        # give *args, **kwargs, so media_type is not strictly necessary. Can be media_type:both
    #     """Total completed movies or series for a user."""
    #     qs = cls.objects.filter(user=user, status=cls.STATUS_COMPLETED)
    #     if media_type:
    #         qs = qs.filter(media__media_type=media_type)
    #     return qs.count()

