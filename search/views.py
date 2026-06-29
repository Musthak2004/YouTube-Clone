from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from videos.models import Video
from channels.models import Channel
from .models import SearchHistory


class SearchView(View):
    template_name = 'search/search_results.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()

        video_results   = Video.objects.none()
        channel_results = Channel.objects.none()

        if query:
            video_results = Video.objects.filter(
                title__icontains=query
            ).order_by('-uploaded_at')

            channel_results = Channel.objects.filter(
                name__icontains=query
            ).order_by('-created_at')

            # History save — logged in users மட்டும்
            if request.user.is_authenticated:
                history, created = SearchHistory.objects.get_or_create(
                    user=request.user,
                    query=query
                )
                if not created:
                    # Already exists — searched_at refresh பண்ணு
                    history.searched_at = timezone.now()
                    history.save()

        recent_history = []
        if request.user.is_authenticated:
            recent_history = SearchHistory.objects.filter(
                user=request.user
            ).order_by('-searched_at')[:8]

        return render(request, self.template_name, {
            'query':           query,
            'video_results':   video_results,
            'channel_results': channel_results,
            'video_count':     video_results.count(),
            'channel_count':   channel_results.count(),
            'total_count':     video_results.count() + channel_results.count(),
            'recent_history':  recent_history,
        })


class ClearSearchHistoryView(View):
    def post(self, request):
        if request.user.is_authenticated:
            SearchHistory.objects.filter(user=request.user).delete()
        return redirect('search')


class DeleteSearchHistoryView(View):
    def post(self, request, pk):
        SearchHistory.objects.filter(pk=pk, user=request.user).delete()
        return redirect('search')