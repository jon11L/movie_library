from django.db import models
import django.utils.timezone as timezone
from django.core.exceptions import ValidationError

from core.models import BaseModel
from user.models import User
from movie.models import Movie
from serie.models import Serie

# Create your models here.
class Comment(BaseModel):
    '''Comment model to store comments made by users on movies or series'''

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='comments')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    body = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(movie__isnull=False, serie__isnull=True) |
                    models.Q(movie__isnull=True, serie__isnull=False)
            ),
                name="only_one_content_type_per_comment"
            ),
        ]


    def __str__(self):
        return (
            f"{self.user.username} commented on {self.kind} ({self.content_object}) "
            f"at {self.created_at:%Y-%m-%d %H%M}:"
            f"'{self.body[:50]}'..."
            )

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
            raise ValidationError("Comment can only reference either a Movie or a Serie, not both.")
        if not self.movie and not self.serie:
            raise ValidationError("comment must reference 1 model, either Movie or Serie.")
