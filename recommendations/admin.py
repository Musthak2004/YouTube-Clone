from django.contrib import admin
from .models import VideoTag, VideoTagMap, UserInterest


@admin.register(VideoTag)
class VideoTagAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)


@admin.register(VideoTagMap)
class VideoTagMapAdmin(admin.ModelAdmin):
    list_display  = ('video', 'tag')
    search_fields = ('video__title', 'tag__name')
    list_filter   = ('tag',)


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display  = ('user', 'tag', 'score')
    search_fields = ('user__username', 'tag__name')
    list_filter   = ('tag',)
    ordering      = ('-score',)