from django.db import models
from django.conf import settings
from django.urls import reverse


class Channel(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='channel'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    banner = models.ImageField(upload_to='channel_banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('channel_detail', kwargs={'pk': self.pk})