from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment
from notifications.models import Notification
from subscriptions.models import Subscription
from videos.models import Video, VideoReaction


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
        verb="commented",
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
        verb="subscribed",
    )


@receiver(post_save, sender=VideoReaction)
def notify_on_like(sender, instance, created, **kwargs):
    """Notify video uploader when someone likes their video."""
    # Only notify on 'like' reactions
    if instance.reaction != "like":
        return

    video = instance.video
    recipient = video.uploader
    actor = instance.user

    # Don't notify yourself
    if actor == recipient:
        return

    # Avoid duplicate notifications for the same actor+video
    already_exists = Notification.objects.filter(
        recipient=recipient,
        actor=actor,
        verb="liked",
        target_video=video,
    ).exists()

    if not already_exists:
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            verb="liked",
            target_video=video,
        )


@receiver(post_save, sender=Video)
def notify_on_video_upload(sender, instance, created, **kwargs):
    """Notify all subscribers when a channel uploads a new video."""
    if not created:
        return

    uploader = instance.uploader

    # Find all subscribers of this uploader
    subscriptions = Subscription.objects.filter(channel=uploader)

    for sub in subscriptions:
        recipient = sub.user
        # Don't notify yourself
        if recipient == uploader:
            continue

        Notification.objects.create(
            recipient=recipient,
            actor=uploader,
            verb="uploaded",
            target_video=instance,
        )
