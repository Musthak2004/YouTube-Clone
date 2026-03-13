from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from subscriptions.models import Subscription
from .models import Video, VideoView


class VideoListView(ListView):
    model = Video
    template_name = "videos/video_list.html"
    context_object_name = "videos"
    ordering = ['-uploaded_at']
    paginate_by = 10


class VideoDetailView(DetailView):
    model = Video
    template_name = 'videos/video_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        video = self.object
        user  = self.request.user

        # Subscriber count
        ctx['subscriber_count'] = video.uploader.subscribers_list.count()

        # Is subscribed?
        ctx['is_subscribed'] = (
            user.is_authenticated and
            Subscription.objects.filter(user=user, channel=video.uploader).exists()
        )

        # User reaction
        ctx['user_reaction'] = None
        if user.is_authenticated:
            reaction = video.reactions.filter(user=user).first()
            ctx['user_reaction'] = reaction.reaction if reaction else None

        # Related / recent videos
        ctx['related_videos'] = (
            Video.objects.filter(channel=video.channel)
            .exclude(pk=video.pk)
            .order_by('-uploaded_at')[:10]
        )

        return ctx


class VideoCreateView(LoginRequiredMixin, CreateView):
    model = Video
    template_name = "videos/video_create.html"
    fields = ['title', 'description', 'video_file', 'thumbnail']

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)


class VideoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Video
    template_name = "videos/video_update.html"
    fields = ['title', 'description', 'video_file', 'thumbnail']

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

    def test_func(self):
        video = self.get_object()
        return self.request.user == video.uploader


class VideoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Video
    template_name = "videos/video_delete.html"
    context_object_name = "video"
    success_url = reverse_lazy("video_list")

    def test_func(self):
        video = self.get_object()
        return self.request.user == video.uploader