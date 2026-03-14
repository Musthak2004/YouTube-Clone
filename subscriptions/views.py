from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()


class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = "subscriptions/subscription_list.html"
    context_object_name = "subscriptions"

    def get_queryset(self):
        return Subscription.objects.filter(
            user=self.request.user
        ).select_related('channel').order_by("-subscribed_at")


class ToggleSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, channel_pk):
        channel = get_object_or_404(User, pk=channel_pk)

        if request.user == channel:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        subscription = Subscription.objects.filter(
            user=request.user,
            channel=channel
        )

        if subscription.exists():
            subscription.delete()
        else:
            Subscription.objects.create(
                user=request.user,
                channel=channel
            )

        return redirect(request.META.get("HTTP_REFERER", "/"))