from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Subscription(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
    )

    channel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscribers_list"
    )

    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "channel"],
                name="unique_subscription"
            )
        ]

    def clean(self):
        if self.user == self.channel:
            raise ValidationError("You cannot subscribe to yourself.")

    def __str__(self):
        return f"{self.user} subscribed to {self.channel}"