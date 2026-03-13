from django.urls import path
from .views import (
    ChannelListView,
    ChannelDetailView,
    ChannelUpdateView,
    ChannelDeleteView,
    ChannelCreateView
)

urlpatterns = [
    path('', ChannelListView.as_view(), name='channel_list'),
    path('create/', ChannelCreateView.as_view(), name='channel_create'),
    path('<int:pk>/', ChannelDetailView.as_view(), name='channel_detail'),
    path('<int:pk>/update/', ChannelUpdateView.as_view(), name='channel_update'),
    path('<int:pk>/delete/', ChannelDeleteView.as_view(), name='channel_delete'),
]