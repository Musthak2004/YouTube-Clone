from django.urls import path

from .views import (AddToPlaylistView, PlaylistCreateView, PlaylistDeleteView,
                    PlaylistDetailView, PlaylistListView, PlaylistUpdateView,
                    ReorderPlaylistItemsView)

urlpatterns = [
    path("", PlaylistListView.as_view(), name="playlist_list"),
    path("create/", PlaylistCreateView.as_view(), name="playlist_create"),
    path("<int:pk>/", PlaylistDetailView.as_view(), name="playlist_detail"),
    path("<int:pk>/update/", PlaylistUpdateView.as_view(), name="playlist_update"),
    path("<int:pk>/delete/", PlaylistDeleteView.as_view(), name="playlist_delete"),
    path("<int:pk>/add-video/", AddToPlaylistView.as_view(), name="playlist_add_video"),
    path(
        "<int:pk>/reorder/", ReorderPlaylistItemsView.as_view(), name="playlist_reorder"
    ),
]
