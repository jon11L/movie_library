from django.db import models
import django.utils.timezone as timezone
from django.core.exceptions import ValidationError

from core.models import BaseModel
from user.models import User
from media_library.models import Media


# Create your models here.
class Comment(BaseModel):
    '''Comment model to store comments made by users on Media'''
    # if user deleted -> DO_NOTHING. Then need to set 'user-deleted' as name instead?
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, null=False, blank=False, related_name='comments')
    body = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.user.username if self.user else 'Deleted-User'} commented on ({self.media}) "
            f"at {self.created_at:%Y-%m-%d %H%M}:"
            f" '{self.body[:50]}'..."
            )


class Like(BaseModel):
    #need field: user who likes , user who's comment is being liked?
    comment = models.ForeignKey(Comment, to_field='id', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE, related_name='comment_likes')

    class Meta:
        db_table = "comment_like"
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        unique_together = ('user', 'comment')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked {self.comment.pk}"


# For the views adding/removing Likes:
# like, created = Like.objects.get_or_create(user=request.user, comment=comment)
# if not created:
#     like.delete()  # already liked — remove it
#     liked = False
# else:
#     liked = True
# return JsonResponse({'liked': liked, 'count': comment.likes.count()})
