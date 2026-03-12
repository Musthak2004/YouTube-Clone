from django.urls import path
from .views import (
    ChannelListView,
    ChannelDetailView,
    ChannelUpdateView,
    ChannelDeleteView
)

urlpatterns = [
    path('channels/', ChannelListView.as_view(), name='channel_list'),
    path('<int:pk>/', ChannelDetailView.as_view(), name='channel_detail'),
    path('<int:pk>/update/', ChannelUpdateView.as_view(), name='channel_update'),
    path('<int:pk>/delete/', ChannelDeleteView.as_view(), name='channel_delete'),
]