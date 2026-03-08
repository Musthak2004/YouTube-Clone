from django.urls import path
from .views import CommentListView

urlpatterns = [
    path("comments/", CommentListView.as_view(), name="comment_list"),
]