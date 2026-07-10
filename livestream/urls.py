from django.urls import path

from . import views

urlpatterns = [
    path("", views.StreamDashboardView.as_view(), name="stream_dashboard"),
    path("go-live/", views.GoLiveView.as_view(), name="go_live"),
    path("end/<pk>/", views.EndStreamView.as_view(), name="end_stream"),
    path("watch/<pk>/", views.WatchStreamView.as_view(), name="watch_stream"),
    path("settings/", views.StreamSettingsView.as_view(), name="stream_settings"),
    path("<pk>/chat/", views.ChatMessageAPIView.as_view(), name="stream_chat"),
]
