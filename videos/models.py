from django.db import models
from django.conf import settings
from django.urls import reverse


class Video(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos',
        db_index=True
    )
    channel = models.ForeignKey(
        'channels.Channel',
        on_delete=models.CASCADE,
        related_name='videos',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    views = models.PositiveIntegerField(default=0, db_index=True)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('video_detail', args=[str(self.id)])

    @property
    def video_url(self):
        if not self.video_file:
            return None
        return self.video_file.url


class VideoReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_reactions'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'video'],
                name='unique_user_video_reaction'
            )
        ]

    def __str__(self):
        return f"{self.user} {self.reaction}d {self.video}"


class VideoView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='video_views'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='view_records'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.video.title} viewed"