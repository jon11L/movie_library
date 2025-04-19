from django.db import models

# from movie.models import Movie
from user.models import User


# Create your models here.
class Comment(models.Model):

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
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return (
            f"{self.user.username} commented on {self.content_type}({self.object_id}) "
            f"at {self.created_at:%Y-%m-%d %H%M}:"
            f"'{self.body[:50]}'..."
            )

    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

