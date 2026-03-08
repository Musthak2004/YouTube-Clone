from django.contrib import admin
from .models import Comment

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'text', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'video__title', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Comment, CommentAdmin)
