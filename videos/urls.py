from django.urls import path
from .views import VideoListView, VideoDetailView, VideoUpdateView, VideoDeleteView, VideoCreateView, VideoReactionView, LikedVideosView

urlpatterns = [
    path('', VideoListView.as_view(), name='video_list'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    path('<int:pk>/update/', VideoUpdateView.as_view(), name='video_update'),
    path('<int:pk>/delete/', VideoDeleteView.as_view(), name='video_delete'),
    path('create/', VideoCreateView.as_view(), name='video_create'),
    path('<int:pk>/reaction/', VideoReactionView.as_view(), name='video_reaction'),
    path('liked/', LikedVideosView.as_view(), name='liked_videos'),
]