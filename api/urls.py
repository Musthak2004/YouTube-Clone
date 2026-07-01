from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, ChannelViewSet, TagViewSet, MeView

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='api-video')
router.register(r'channels', ChannelViewSet, basename='api-channel')
router.register(r'tags', TagViewSet, basename='api-tag')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', MeView.as_view(), name='api-me'),
    path('auth/', include('rest_framework.urls')),
]
