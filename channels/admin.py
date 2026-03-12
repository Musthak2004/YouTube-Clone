from django.contrib import admin
from .models import Channel, Subscription

# Channel admin
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

# Subscription admin
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'channel', 'subscribed_at')
    search_fields = ('subscriber__username', 'channel__name')
    list_filter = ('subscribed_at',)
    readonly_fields = ('subscribed_at',)
    ordering = ('-subscribed_at',)