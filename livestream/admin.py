from django.contrib import admin

from .models import ChatMessage, Stream, StreamKey


@admin.register(StreamKey)
class StreamKeyAdmin(admin.ModelAdmin):
    list_display = ("channel", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("channel__name", "channel__owner__username")
    readonly_fields = ("key", "created_at")


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("title", "channel", "is_live", "viewer_count", "started_at")
    list_filter = ("is_live",)
    search_fields = ("title", "channel__name")
    date_hierarchy = "started_at"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("stream", "user", "short_message", "sent_at")
    search_fields = ("message", "user__username", "stream__title")

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message[:60]
