from django.urls import path
from .views import VideoListView, VideoDetailView, VideoUpdateView, VideoDeleteView, VideoCreateView

urlpatterns = [
    path('', VideoListView.as_view(), name='video_list'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    path('<int:pk>/update/', VideoUpdateView.as_view(), name='video_update'),
    path('<int:pk>/delete/', VideoDeleteView.as_view(), name='video_delete'),
    path('create/', VideoCreateView.as_view(), name='video_create'),
]