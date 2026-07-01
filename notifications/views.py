from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView

from notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor', 'target_video')


class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return JsonResponse({'ok': True})


class UnreadCountView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return JsonResponse({'count': count})
