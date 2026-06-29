from django.urls import path
from .views import (
    CommentListView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView
)

urlpatterns = [
    path("", CommentListView.as_view(), name="comment_list"),
    path("videos/<int:video_pk>/comment/", CommentCreateView.as_view(), name="comment_create"),
    path("<int:pk>/edit/", CommentUpdateView.as_view(), name="comment_edit"),
    path("<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"),
]