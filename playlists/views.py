from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import PlaylistForm
from .models import Playlist, PlaylistItem


class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = "playlists/playlist_list.html"
    context_object_name = "playlists"
    paginate_by = 12

    def get_queryset(self):
        return (
            Playlist.objects.filter(owner=self.request.user)
            .annotate(item_count=Count("items"))
            .order_by("-updated_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_videos"] = PlaylistItem.objects.filter(
            playlist__owner=self.request.user
        ).count()
        return ctx


class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = "playlists/playlist_detail.html"
    context_object_name = "playlist"

    def get_queryset(self):
        return Playlist.objects.select_related("owner").prefetch_related(
            "items__video__uploader"
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Private → owner only
        if self.object.visibility == "private" and self.object.owner != request.user:
            return redirect("playlist_list")
        # Unlisted → only accessible with the link
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        playlist = self.object
        ctx["is_owner"] = (
            self.request.user.is_authenticated and self.request.user == playlist.owner
        )
        items = playlist.items.select_related("video__uploader").all()
        from django.core.paginator import Paginator

        paginator = Paginator(items, 12)
        page_num = self.request.GET.get("page", 1)
        ctx["playlist_items"] = paginator.get_page(page_num)
        ctx["total_items"] = paginator.count
        return ctx


class PlaylistCreateView(LoginRequiredMixin, CreateView):
    model = Playlist
    template_name = "playlists/playlist_create.html"
    form_class = PlaylistForm
    success_url = reverse_lazy("playlist_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # JSON response for AJAX (inline creation in Save modal)
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "id": self.object.pk,
                    "title": self.object.title,
                }
            )
        return response

    def form_invalid(self, form):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Invalid form data"}, status=400)
        return super().form_invalid(form)


class PlaylistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Playlist
    template_name = "playlists/playlist_update.html"
    form_class = PlaylistForm
    success_url = reverse_lazy("playlist_list")

    def test_func(self):
        return self.request.user == self.get_object().owner


class PlaylistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Playlist
    template_name = "playlists/playlist_delete.html"
    context_object_name = "playlist"
    success_url = reverse_lazy("playlist_list")

    def test_func(self):
        return self.request.user == self.get_object().owner


class AddToPlaylistView(LoginRequiredMixin, View):
    """Toggles which playlists a video belongs to.

    POST data:
      - playlist_ids: list of playlist PKs the video SHOULD be in.
    """

    def post(self, request, pk):
        from videos.models import Video

        video = get_object_or_404(Video, pk=pk)
        selected_ids = set(map(int, request.POST.getlist("playlist_ids")))
        user_playlist_ids = set(
            Playlist.objects.filter(owner=request.user).values_list("pk", flat=True)
        )

        # Only operate on playlists the user owns
        valid_ids = selected_ids & user_playlist_ids

        # Remove video from playlists not in the selection
        PlaylistItem.objects.filter(
            playlist__owner=request.user,
            video=video,
        ).exclude(playlist__pk__in=valid_ids).delete()

        # Add video to newly selected playlists
        for pl_id in valid_ids:
            PlaylistItem.objects.get_or_create(
                playlist_id=pl_id,
                video=video,
                defaults={"order": 0},
            )

        return redirect(video.get_absolute_url())


class ReorderPlaylistItemsView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Reorder items in a playlist.

    POST data:
      - item_ids: ordered list of PlaylistItem PKs.
    """

    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        item_ids = request.POST.getlist("item_ids")
        for idx, item_id in enumerate(item_ids):
            PlaylistItem.objects.filter(pk=item_id, playlist=playlist).update(order=idx)
        return redirect(playlist.get_absolute_url())

    def test_func(self):
        return self.request.user == self.get_object().owner


# Need models.Count for the annotation
