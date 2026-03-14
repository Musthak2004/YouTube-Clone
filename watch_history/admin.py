from django.contrib import admin
from .models import WatchHistory


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display  = ('user', 'video', 'watched_at', 'watch_duration')
    search_fields = ('user__username', 'video__title')
    list_filter   = ('watched_at',)
    readonly_fields = ('user', 'video', 'watched_at', 'watch_duration')
    ordering      = ('-watched_at',)