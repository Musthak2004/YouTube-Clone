from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Comment

# Create your views here.
class CommentListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = "comments/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).order_by("-created_at")
