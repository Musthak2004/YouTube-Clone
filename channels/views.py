from django.views.generic import ListView
from .models import Channel, Subscription

# Create your views here.
class ChannelListView(ListView):
    model = Channel
    template_name = 'channels/channel_list.html'
    context_object_name = 'channels'
    ordering = ['-created_at']

