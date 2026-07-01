from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment
from subscriptions.models import Subscription
from notifications.models import Notification


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return
    video = instance.video
    recipient = video.uploader
    actor = instance.user
    # Don't notify yourself
    if actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb='commented',
        target_video=video,
    )


@receiver(post_save, sender=Subscription)
def notify_on_subscribe(sender, instance, created, **kwargs):
    if not created:
        return
    recipient = instance.channel
    actor = instance.user
    # Don't notify yourself
    if actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb='subscribed',
    )
