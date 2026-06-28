from django.db import models
from django.conf import settings
from django.urls import reverse
from cloudinary.utils import cloudinary_url


class Video(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
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
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('video_detail', args=[str(self.id)])

    @property
    def video_url(self):
        if not self.video_file:
            return None
        url, _ = cloudinary_url(
            self.video_file.name,
            resource_type='video',
            secure=True
        )
        return url


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
        unique_together = ('user', 'video')

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
        related_name='view_view_counts'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} viewed"