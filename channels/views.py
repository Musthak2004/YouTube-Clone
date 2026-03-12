from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Channel
from videos.models import Video


# Channel List
class ChannelListView(ListView):
    model = Channel
    template_name = 'channels/channel_list.html'
    context_object_name = 'channels'
    ordering = ['-created_at']


# Channel Detail
class ChannelDetailView(DetailView):
    model = Channel
    template_name = "channels/channel_detail.html"
    context_object_name = "channel"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        channel = self.get_object()

        videos = Video.objects.filter(channel=channel).order_by("-created_at")

        context["videos"] = videos
        context["video_count"] = videos.count()
        context["subscriber_count"] = channel.subscribers.count()

        return context


# Channel Update
class ChannelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Channel
    fields = ['name', 'description', 'banner']
    template_name = 'channels/channel_form.html'

    def test_func(self):
        channel = self.get_object()
        return self.request.user == channel.owner


# Channel Delete
class ChannelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Channel
    template_name = 'channels/channel_confirm_delete.html'
    success_url = reverse_lazy('channel_list')

    def test_func(self):
        channel = self.get_object()
        return self.request.user == channel.owner