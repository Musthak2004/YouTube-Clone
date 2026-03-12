from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Channel


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_channel(sender, instance, created, **kwargs):
    if created:
        Channel.objects.create(
            owner=instance,
            name=f"{instance.username}'s Channel"
        )