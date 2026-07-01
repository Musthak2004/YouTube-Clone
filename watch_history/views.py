from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import WatchHistory
from videos.models import Video


class WatchHistoryView(LoginRequiredMixin, ListView):
    template_name = 'watch_history/watch_history.html'
    context_object_name = 'history'
    paginate_by = 16

    def get_queryset(self):
        return WatchHistory.objects.filter(
            user=self.request.user
        ).select_related('video', 'video__uploader').order_by('-watched_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_count'] = WatchHistory.objects.filter(
            user=self.request.user
        ).count()
        return ctx


class ClearWatchHistoryView(LoginRequiredMixin, View):
    def post(self, request):
        WatchHistory.objects.filter(user=request.user).delete()
        return redirect('watch_history')


class RemoveWatchHistoryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        WatchHistory.objects.filter(pk=pk, user=request.user).delete()
        return redirect(request.META.get('HTTP_REFERER', 'watch_history'))


@method_decorator(csrf_exempt, name='dispatch')
class UpdateWatchProgressView(LoginRequiredMixin, View):
    """Receives periodic watch-duration updates from the video player."""
    def post(self, request, video_id):
        import json
        try:
            data = json.loads(request.body)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid body'}, status=400)

        duration = data.get('watch_duration')
        if not isinstance(duration, (int, float)):
            return JsonResponse({'error': 'watch_duration required'}, status=400)

        # Update the most recent watch-history entry for this user + video
        updated = WatchHistory.objects.filter(
            user=request.user,
            video_id=video_id,
        ).update(watch_duration=int(duration))

        return JsonResponse({'ok': True, 'updated': updated > 0})