from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .forms import ChannelForm
from .models import Channel


class ChannelListView(ListView):
    model = Channel
    template_name = 'channels/channel_list.html'
    context_object_name = 'channels'
    ordering = ['-created_at']
    paginate_by = 10


class ChannelDetailView(DetailView):
    model = Channel
    template_name = 'channels/channel_detail.html'
    context_object_name = 'channel'


class ChannelCreateView(LoginRequiredMixin, CreateView):
    model = Channel
    form_class = ChannelForm
    template_name = 'channels/channel_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ChannelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Channel
    form_class = ChannelForm
    template_name = 'channels/channel_update.html'

    def test_func(self):
        channel = self.get_object()
        return self.request.user == channel.owner


class ChannelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Channel
    template_name = 'channels/channel_delete.html'
    context_object_name = 'channel'
    success_url = reverse_lazy('channel_list')

    def test_func(self):
        channel = self.get_object()
        return self.request.user == channel.owner