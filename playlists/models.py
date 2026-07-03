from django.conf import settings
from django.db import models
from django.urls import reverse


class Playlist(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("unlisted", "Unlisted"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="playlists",
        db_index=True,
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("playlist_detail", args=[str(self.pk)])


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="items",
    )
    video = models.ForeignKey(
        "videos.Video",
        on_delete=models.CASCADE,
        related_name="playlist_items",
    )
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "video"],
                name="unique_playlist_video",
            )
        ]

    def __str__(self):
        return f"{self.video.title} in {self.playlist.title}"
