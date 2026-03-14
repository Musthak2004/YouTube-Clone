from django.db import models
from django.conf import settings


class WatchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watch_history'
    )
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='watch_history'
    )
    watched_at = models.DateTimeField(auto_now_add=True)
    watch_duration = models.IntegerField(default=0, help_text="Seconds watched")

    class Meta:
        ordering = ['-watched_at']
        verbose_name_plural = 'Watch Histories'

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"

    @property
    def duration_percent(self):
        if self.video.duration and self.video.duration > 0:
            return round((self.watch_duration / self.video.duration) * 100, 1)
        return 0