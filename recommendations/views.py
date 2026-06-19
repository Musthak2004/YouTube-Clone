from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from videos.models import Video
from .models import VideoTag, VideoTagMap, UserInterest


class TagVideoListView(ListView):
    template_name = 'recommendations/tag_videos.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(VideoTag, pk=self.kwargs['pk'])

        # User interest score increment
        if self.request.user.is_authenticated:
            interest, _ = UserInterest.objects.get_or_create(
                user=self.request.user,
                tag=self.tag
            )
            interest.score += 1
            interest.save()

        return Video.objects.filter(
            tags__tag=self.tag
        ).order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag'] = self.tag
        ctx['all_tags'] = VideoTag.objects.all().order_by('name')
        ctx['tag_video_count'] = ctx['paginator'].count
        return ctx