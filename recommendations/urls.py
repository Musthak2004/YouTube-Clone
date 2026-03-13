from django.urls import path
from .views import TagVideoListView

urlpatterns = [
    path('tag/<int:pk>/', TagVideoListView.as_view(), name='tag_videos'),
]