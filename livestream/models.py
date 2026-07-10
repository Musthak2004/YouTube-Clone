import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from channels.models import Channel


class StreamKey(models.Model):
    channel = models.OneToOneField(
        Channel, on_delete=models.CASCADE, related_name="stream_key"
    )
    key = models.CharField(
        max_length=64, unique=True, default=uuid.uuid4().hex, editable=False
    )
    display_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "stream keys"

    def __str__(self):
        return f"StreamKey for {self.channel.name}"

    def regenerate(self):
        self.key = uuid.uuid4().hex
        self.save(update_fields=["key"])


class Stream(models.Model):
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="streams"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to="stream_thumbnails/", blank=True, null=True)
    stream_key = models.ForeignKey(
        StreamKey, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_live = models.BooleanField(default=False, db_index=True)
    viewer_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            models.OrderBy(models.F("started_at"), descending=True, nulls_first=True),
            "-created_at",
        ]

    def __str__(self):
        return f"{self.title} ({'LIVE' if self.is_live else 'ended'})"

    def get_absolute_url(self):
        return reverse("watch_stream", kwargs={"pk": self.pk})

    @property
    def duration(self):
        """Duration in seconds, or 0 if not started/ended."""
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        return 0


class ChatMessage(models.Model):
    stream = models.ForeignKey(
        Stream, on_delete=models.CASCADE, related_name="chat_messages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    message = models.TextField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["stream", "sent_at"]),
        ]

    def clean(self):
        if len(self.message) > 500:
            raise ValidationError({"message": "Message cannot exceed 500 characters."})

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
