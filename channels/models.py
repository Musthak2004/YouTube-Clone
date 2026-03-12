from django.urls import reverse

from django.db import models
from django.conf import settings

# Create your models here.
class Channel(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='channel')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    banner = models.ImageField(upload_to='channel_banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('channel_detail', kwargs={'pk': self.pk})

class Subscription(models.Model):
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='channel_subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'channel')

    def __str__(self):
        return f"{self.subscriber.username} - {self.channel.name}"