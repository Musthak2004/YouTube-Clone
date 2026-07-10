from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from notifications.models import Notification
from subscriptions.models import Subscription

from .forms import StartStreamForm, StreamSettingsForm
from .models import ChatMessage, Stream, StreamKey


class StreamDashboardView(LoginRequiredMixin, ListView):
    """Show all streams for the current user's channel."""

    model = Stream
    template_name = "livestream/stream_dashboard.html"
    context_object_name = "streams"
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self.request.user, "channel"):
            return Stream.objects.none()
        return (
            Stream.objects.filter(channel=self.request.user.channel)
            .select_related("channel", "channel__owner")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if hasattr(user, "channel"):
            ctx["channel"] = user.channel
            ctx["active_stream"] = self.get_queryset().filter(is_live=True).first()
            ctx["has_stream_key"] = StreamKey.objects.filter(
                channel=user.channel, is_active=True
            ).exists()
        else:
            ctx["channel"] = None
            ctx["active_stream"] = None
            ctx["has_stream_key"] = False
        return ctx


class GoLiveView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Start a new live stream."""

    model = Stream
    template_name = "livestream/go_live.html"
    form_class = StartStreamForm

    def test_func(self):
        return hasattr(self.request.user, "channel")

    def form_valid(self, form):
        form.instance.channel = self.request.user.channel
        form.instance.is_live = True
        form.instance.started_at = timezone.now()
        form.instance.stream_key = form.resolved_key

        response = super().form_valid(form)

        # Notify subscribers
        self._notify_subscribers(form.instance)

        return response

    def get_success_url(self):
        return reverse_lazy("watch_stream", kwargs={"pk": self.object.pk})

    def _notify_subscribers(self, stream):
        """Notify all subscribers that the channel went live."""
        uploader = self.request.user
        subs = Subscription.objects.filter(channel=uploader).select_related("user")

        notifications = []
        for sub in subs:
            if sub.user != uploader:
                notifications.append(
                    Notification(
                        recipient=sub.user,
                        actor=uploader,
                        verb="went_live",
                    )
                )

        if notifications:
            Notification.objects.bulk_create(notifications)


class EndStreamView(LoginRequiredMixin, UserPassesTestMixin, View):
    """End an active live stream."""

    def test_func(self):
        stream = get_object_or_404(Stream, pk=self.kwargs["pk"])
        return (
            hasattr(self.request.user, "channel")
            and stream.channel == self.request.user.channel
        )

    def post(self, request, pk):
        stream = get_object_or_404(Stream, pk=pk)
        stream.is_live = False
        stream.ended_at = timezone.now()
        stream.viewer_count = 0
        stream.save(update_fields=["is_live", "ended_at", "viewer_count"])
        return redirect("stream_dashboard")


class WatchStreamView(DetailView):
    """Watch a live stream (public, no login required)."""

    model = Stream
    template_name = "livestream/watch_stream.html"
    context_object_name = "stream"

    def get_queryset(self):
        return Stream.objects.select_related(
            "channel", "channel__owner"
        ).prefetch_related("chat_messages")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        stream = self.object

        # Increment viewer count if live
        if stream.is_live:
            Stream.objects.filter(pk=stream.pk).update(
                viewer_count=stream.viewer_count + 1
            )

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        stream = self.object
        user = self.request.user

        chat_qs = stream.chat_messages.select_related("user").order_by("sent_at")[:50]
        ctx["recent_chat"] = list(chat_qs)

        ctx["subscriber_count"] = Subscription.objects.filter(
            channel=stream.channel.owner
        ).count()

        ctx["is_subscribed"] = (
            user.is_authenticated
            and Subscription.objects.filter(
                user=user, channel=stream.channel.owner
            ).exists()
        )

        ctx["is_owner"] = (
            user.is_authenticated
            and hasattr(user, "channel")
            and user.channel == stream.channel
        )

        return ctx


class StreamSettingsView(LoginRequiredMixin, UpdateView):
    """Manage stream key settings."""

    model = StreamKey
    template_name = "livestream/stream_settings.html"
    form_class = StreamSettingsForm
    success_url = reverse_lazy("stream_settings")

    def get_object(self, queryset=None):
        channel = getattr(self.request.user, "channel", None)
        if not channel:
            return None
        obj, _ = StreamKey.objects.get_or_create(
            channel=channel,
            defaults={
                "key": __import__("uuid").uuid4().hex,
                "display_name": channel.name,
            },
        )
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.get_object()
        if obj:
            # Only show the raw key on GET (one-time display)
            ctx["show_key"] = True
            ctx["raw_key"] = obj.key
        ctx["has_channel"] = hasattr(self.request.user, "channel")
        return ctx

    def form_valid(self, form):
        obj = form.instance
        if form.cleaned_data.get("regenerate_key"):
            obj.regenerate()
        form.save()
        return redirect(self.success_url)


class ChatMessageAPIView(LoginRequiredMixin, View):
    """API endpoint for live chat messages."""

    def get(self, request, pk):
        """Return messages since ?after=<message_id>."""
        stream = get_object_or_404(Stream, pk=pk)
        after = request.GET.get("after")
        messages_qs = (
            ChatMessage.objects.filter(stream=stream)
            .select_related("user", "user__channel")
            .order_by("sent_at")
        )

        if after:
            try:
                after_id = int(after)
                messages_qs = messages_qs.filter(id__gt=after_id)
            except (ValueError, TypeError):
                pass

        messages_data = []
        for msg in messages_qs[:50]:
            messages_data.append(
                {
                    "id": msg.id,
                    "user": msg.user.username,
                    "avatar": (
                        msg.user.profile_picture.url
                        if msg.user.profile_picture
                        else None
                    ),
                    "message": msg.message,
                    "sent_at": msg.sent_at.isoformat(),
                }
            )

        return JsonResponse({"messages": messages_data, "stream_live": stream.is_live})

    def post(self, request, pk):
        """Post a chat message."""
        stream = get_object_or_404(Stream, pk=pk)

        if not stream.is_live:
            return JsonResponse({"error": "Stream is not live."}, status=400)

        message = request.POST.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        if len(message) > 500:
            return JsonResponse({"error": "Message too long."}, status=400)

        # Rate limit: 10 messages in 30s per user per stream
        cutoff = timezone.now() - timezone.timedelta(seconds=30)
        recent_count = ChatMessage.objects.filter(
            stream=stream, user=request.user, sent_at__gte=cutoff
        ).count()

        if recent_count >= 10:
            return JsonResponse(
                {"error": "You're sending messages too fast. Slow down."},
                status=429,
            )

        chat_msg = ChatMessage.objects.create(
            stream=stream, user=request.user, message=message
        )

        return JsonResponse(
            {
                "id": chat_msg.id,
                "user": chat_msg.user.username,
                "message": chat_msg.message,
                "sent_at": chat_msg.sent_at.isoformat(),
            },
            status=201,
        )
