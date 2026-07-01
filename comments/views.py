from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from .models import Comment
from videos.models import Video


class CommentListView(LoginRequiredMixin, ListView):

    model = Comment
    template_name = "comments/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        return Comment.objects.select_related(
            'video', 'video__uploader'
        ).filter(
            user=self.request.user
        ).order_by("-created_at")


class CommentCreateView(LoginRequiredMixin, CreateView):

    model = Comment
    template_name = "comments/comment_create.html"
    fields = ["text"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['video'] = get_object_or_404(Video, pk=self.kwargs["video_pk"])
        parent_pk = self.request.GET.get('parent') or self.request.POST.get('parent')
        if parent_pk:
            ctx['parent_comment'] = get_object_or_404(
                Comment, pk=parent_pk, video=ctx['video']
            )
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.video = get_object_or_404(
            Video, pk=self.kwargs["video_pk"]
        )
        parent_pk = self.request.POST.get('parent')
        if parent_pk:
            parent = get_object_or_404(
                Comment, pk=parent_pk, video=form.instance.video
            )
            form.instance.parent = parent
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.video.get_absolute_url()


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Comment
    template_name = "comments/comment_edit.html"
    fields = ["text"]

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return self.object.video.get_absolute_url()


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Comment
    template_name = "comments/comment_delete.html"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return self.object.video.get_absolute_url()