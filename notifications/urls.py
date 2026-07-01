from django.urls import path

from notifications import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/read/', views.MarkAsReadView.as_view(), name='mark_as_read'),
    path('unread-count/', views.UnreadCountView.as_view(), name='unread_count'),
]
