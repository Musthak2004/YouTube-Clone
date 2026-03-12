from django.urls import path
from .views import ChannelListView

urlpatterns = [
    path('channels/', ChannelListView.as_view(), name='channel_list'),
]