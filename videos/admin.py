from django.contrib import admin
from .models import Video, VideoReaction, VideoView


class VideoAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "uploader",
        "uploaded_at",
        "views",
    )

    list_filter = (
        "uploaded_at",
    )

    search_fields = (
        "title",
        "description",
        "uploader__username",
    )

    readonly_fields = (
        "uploaded_at",
        "views",
    )

    ordering = (
        "-uploaded_at",
    )


class VideoReactionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "video",
        "reaction",
        "created_at",
    )

    list_filter = (
        "reaction",
        "created_at",
    )

    search_fields = (
        "user__username",
        "video__title",
    )

    ordering = (
        "-created_at",
    )


class VideoViewAdmin(admin.ModelAdmin):

    list_display = (
        "video",
        "user",
        "viewed_at",
    )

    list_filter = (
        "viewed_at",
    )

    search_fields = (
        "video__title",
        "user__username",
    )

    ordering = (
        "-viewed_at",
    )


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoReaction, VideoReactionAdmin)
admin.site.register(VideoView, VideoViewAdmin)