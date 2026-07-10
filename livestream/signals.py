import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.models import Channel
from notifications.models import Notification
from subscriptions.models import Subscription

from .models import StreamKey


@receiver(post_save, sender=Channel)
def create_stream_key(sender, instance, created, **kwargs):
    """Auto-create a StreamKey when a Channel is created."""
    if created:
        StreamKey.objects.create(channel=instance, key=uuid.uuid4().hex)


def notify_subscribers_of_live_stream(stream, actor):
    """Send 'went_live' notifications to all subscribers of the channel owner."""
    subs = Subscription.objects.filter(channel=stream.channel.owner)
    notifications = [
        Notification(recipient=sub.user, actor=actor, verb="went_live")
        for sub in subs
        if sub.user != actor
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
