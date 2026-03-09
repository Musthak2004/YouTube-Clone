from django.contrib import admin
from .models import Subscription

# Register your models here.
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'subscribed_at')
    search_fields = ('user__username', 'channel__username')
    list_filter = ('subscribed_at',)
    ordering = ('-subscribed_at',)

admin.site.register(Subscription, SubscriptionAdmin)
