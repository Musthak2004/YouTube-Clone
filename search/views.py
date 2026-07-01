from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q, Case, When, Value, IntegerField
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
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(uploader__username__icontains=query)
            ).annotate(
                relevance=Case(
                    When(title__iexact=query, then=Value(4)),
                    When(title__istartswith=query, then=Value(3)),
                    When(title__icontains=query, then=Value(2)),
                    When(description__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-relevance', '-uploaded_at').select_related('uploader')

            channel_results = Channel.objects.filter(
                Q(name__icontains=query) |
                Q(owner__username__icontains=query)
            ).order_by('-created_at').select_related('owner')

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