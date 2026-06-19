from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from subscriptions.models import Subscription
from .models import Video, VideoView, VideoReaction

class LikedVideosView(LoginRequiredMixin, ListView):
    template_name = 'videos/liked_videos.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        return Video.objects.filter(
            reactions__user=self.request.user,      # reaction → reactions
            reactions__reaction='like'
        ).order_by('-reactions__id')                # reactions_id → reactions__id (double underscore)

class VideoReactionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video    = get_object_or_404(Video, pk=pk)
        reaction = request.POST.get('reaction')  # 'like' or 'dislike'

        if reaction not in ('like', 'dislike'):
            return redirect(video.get_absolute_url())

        obj, created = VideoReaction.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'reaction': reaction}
        )

        if not created:
            if obj.reaction == reaction:
                # Same button மறுபடியும் click — toggle off (delete)
                obj.delete()
            else:
                # Like → Dislike or vice versa
                obj.reaction = reaction
                obj.save()

        return redirect(video.get_absolute_url())

class VideoListView(ListView):
    model = Video
    template_name = "videos/video_list.html"
    context_object_name = "videos"
    ordering = ['-uploaded_at']
    paginate_by = 10


class VideoDetailView(DetailView):
    model = Video
    template_name = 'videos/video_detail.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Track video view
        VideoView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            video=self.object
        )
        Video.objects.filter(pk=self.object.pk).update(views=self.object.views + 1)

        if request.user.is_authenticated:
            from watch_history.models import WatchHistory
            WatchHistory.objects.create(
                user=request.user,
                video=self.object
            )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        video = self.object
        user  = self.request.user

        ctx['subscriber_count'] = video.uploader.subscribers_list.count()

        ctx['is_subscribed'] = (
            user.is_authenticated and
            Subscription.objects.filter(user=user, channel=video.uploader).exists()
        )

        ctx['user_reaction'] = None
        if user.is_authenticated:
            reaction = video.reactions.filter(user=user).first()
            ctx['user_reaction'] = reaction.reaction if reaction else None

        ctx['related_videos'] = (
            Video.objects.filter(channel=video.channel)
            .exclude(pk=video.pk)
            .order_by('-uploaded_at')[:10]
        )

        ctx['video_tags'] = video.tags.select_related('tag').all()

        return ctx


class VideoCreateView(LoginRequiredMixin, CreateView):
    model = Video
    template_name = "videos/video_create.html"
    fields = ['title', 'description', 'video_file', 'thumbnail']

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        if hasattr(self.request.user, 'channel'):
            form.instance.channel = self.request.user.channel
        response = super().form_valid(form)

        # Tags save
        tag_ids = self.request.POST.getlist('tags')
        for tag_id in tag_ids:
            try:
                from recommendations.models import VideoTag, VideoTagMap
                tag = VideoTag.objects.get(pk=tag_id)
                VideoTagMap.objects.get_or_create(video=self.object, tag=tag)
            except VideoTag.DoesNotExist:
                pass
        return response


class VideoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Video
    template_name = "videos/video_update.html"
    fields = ['title', 'description', 'video_file', 'thumbnail']

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().uploader


class VideoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Video
    template_name = "videos/video_delete.html"
    context_object_name = "video"
    success_url = reverse_lazy("video_list")

    def test_func(self):
        return self.request.user == self.get_object().uploader