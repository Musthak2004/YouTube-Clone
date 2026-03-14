from django.urls import path
from .views import WatchHistoryView, ClearWatchHistoryView, RemoveWatchHistoryView

urlpatterns = [
    path('',              WatchHistoryView.as_view(),       name='watch_history'),
    path('clear/',        ClearWatchHistoryView.as_view(),  name='watch_history_clear'),
    path('<int:pk>/remove/', RemoveWatchHistoryView.as_view(), name='watch_history_remove'),
]