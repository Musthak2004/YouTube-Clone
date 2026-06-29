from django.db import models
from django.conf import settings


class VideoTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VideoTagMap(models.Model):
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='tags'
    )
    tag = models.ForeignKey(
        VideoTag,
        on_delete=models.CASCADE,
        related_name='videos'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['video', 'tag'],
                name='unique_video_tag'
            )
        ]

    def __str__(self):
        return f"{self.video.title} → {self.tag.name}"


class UserInterest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests'
    )
    tag = models.ForeignKey(
        VideoTag,
        on_delete=models.CASCADE,
        related_name='interested_users'
    )
    score = models.IntegerField(default=0)

    class Meta:
        ordering = ['-score']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'tag'],
                name='unique_user_tag_interest'
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.tag.name} ({self.score})"