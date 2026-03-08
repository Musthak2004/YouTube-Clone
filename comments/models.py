from django.db import models
from django.conf import settings
from videos.models import Video


class Comment(models.Model):

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} commented on {self.video}"

    def get_absolute_url(self):
        return self.video.get_absolute_url()