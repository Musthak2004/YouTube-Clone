from django.db import models
from django.conf import settings
from django.urls import reverse
from channels.models import Channel


class Video(models.Model):

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    channel = models.ForeignKey(
        'channels.Channel',
        on_delete=models.CASCADE,
        related_name='videos',
        null=True, blank=True  # optional ஆக வைக்கலாம்
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    video_file = models.FileField(upload_to="videos/")

    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("video_detail", args=[str(self.id)])


class VideoReaction(models.Model):

    REACTION_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_reactions"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    reaction = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "video")

    def __str__(self):
        return f"{self.user} {self.reaction} {self.video}"


class VideoView(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_views"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="view_history"
    )

    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} viewed"