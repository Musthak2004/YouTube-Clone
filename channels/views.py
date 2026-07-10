from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from subscriptions.models import Subscription

from .forms import ChannelForm
from .models import Channel

try:
    from livestream.models import Stream
except ImportError:
    Stream = None


class ChannelListView(ListView):
    model = Channel
    template_name = "channels/channel_list.html"
    context_object_name = "channels"
    paginate_by = 10

    def get_queryset(self):
        return Channel.objects.annotate(
            subscriber_count=Count("owner__subscribers_list")
        ).order_by("-created_at")


class ChannelDetailView(DetailView):
    model = Channel
    template_name = "channels/channel_detail.html"
    context_object_name = "channel"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        channel = self.object
        user = self.request.user

        ctx["subscriber_count"] = Subscription.objects.filter(
            channel=channel.owner
        ).count()

        ctx["video_count"] = channel.videos.count()

        ctx["total_views"] = channel.videos.aggregate(total=Sum("views"))["total"] or 0

        ctx["is_subscribed"] = (
            user.is_authenticated
            and Subscription.objects.filter(user=user, channel=channel.owner).exists()
        )

        if Stream is not None:
            live_qs = Stream.objects.filter(channel=channel, is_live=True)
            ctx["is_live"] = live_qs.exists()
            ctx["live_stream"] = live_qs.first()
        else:
            ctx["is_live"] = False
            ctx["live_stream"] = None

        return ctx


class ChannelCreateView(LoginRequiredMixin, CreateView):
    model = Channel
    form_class = ChannelForm
    template_name = "channels/channel_create.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ChannelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Channel
    form_class = ChannelForm
    template_name = "channels/channel_update.html"

    def test_func(self):
        return self.request.user == self.get_object().owner


class ChannelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Channel
    template_name = "channels/channel_delete.html"
    context_object_name = "channel"
    success_url = reverse_lazy("channel_list")

    def test_func(self):
        return self.request.user == self.get_object().owner
