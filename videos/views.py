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
    template_name = "videos/video_detail.html"
    context_object_name = "video"

    def get_object(self):
        video = super().get_object()

        # Uploader views count பண்ண வேண்டாம்
        if self.request.user != video.uploader:
            video.views += 1
            video.save(update_fields=['views'])

            # Anonymous user handle பண்றோம் safely
            VideoView.objects.create(
                user=self.request.user if self.request.user.is_authenticated else None,
                video=video,
            )

        return video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related videos - same uploader
        context['related_videos'] = (
            Video.objects
            .filter(uploader=self.object.uploader)
            .exclude(id=self.object.id)
            .order_by('-views')[:8]
        )

        # Recent videos fallback
        context['recent_videos'] = (
            Video.objects
            .exclude(id=self.object.id)
            .order_by('-uploaded_at')[:8]
        )

        # Subscription check - uploader's Channel object வேணும்
        if self.request.user.is_authenticated:
            context["is_subscribed"] = Subscription.objects.filter(
                user=self.request.user,
                channel=self.object.uploader  # ✅ Fixed: User → Channel via owner
            ).exists()
        else:
            context["is_subscribed"] = False

        return context


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