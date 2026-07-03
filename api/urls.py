from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ChannelViewSet, MeView, PlaylistViewSet, TagViewSet,
                    VideoViewSet)

router = DefaultRouter()
router.register(r"videos", VideoViewSet, basename="api-video")
router.register(r"channels", ChannelViewSet, basename="api-channel")
router.register(r"tags", TagViewSet, basename="api-tag")
router.register(r"playlists", PlaylistViewSet, basename="api-playlist")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MeView.as_view(), name="api-me"),
    path("auth/", include("rest_framework.urls")),
]
