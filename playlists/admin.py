from django.contrib import admin

from .models import Playlist, PlaylistItem


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "visibility", "item_count", "updated_at"]
    list_filter = ["visibility", "created_at"]
    search_fields = ["title", "owner__username"]

    def item_count(self, obj):
        return obj.items.count()


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ["playlist", "video", "order", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["playlist__title", "video__title"]
