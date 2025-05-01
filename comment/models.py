from django.db import models
import django.utils.timezone as timezone
# from movie.models import Movie
from user.models import User
from core.models import BaseModel

# Create your models here.
class Comment(BaseModel):
    '''Comment model to store comments made by users on movies or series'''

    MOVIE = 'movie'
    SERIE = 'serie'

    CONTENT_TYPE_CHOICES = [
        (MOVIE, 'Movie'),
        (SERIE, 'Serie'),
    ]

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='comments')
    content_type = models.CharField(max_length=25, choices=CONTENT_TYPE_CHOICES, null=False)        
    object_id = models.PositiveIntegerField(null=False)
    body = models.TextField(blank=False, null=False)

    
    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.user.username} commented on {self.content_type}({self.object_id}) "
            f"at {self.created_at:%Y-%m-%d %H%M}:"
            f"'{self.body[:50]}'..."
            )
