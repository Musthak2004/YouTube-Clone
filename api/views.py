from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from channels.models import Channel
from playlists.models import Playlist, PlaylistItem
from recommendations.models import VideoTag
from videos.models import Video, VideoReaction

from .serializers import (AddToPlaylistSerializer, ChannelSerializer,
                          CommentCreateSerializer, CommentSerializer,
                          PlaylistSerializer, ReactionSerializer,
                          UserSerializer, VideoDetailSerializer,
                          VideoListSerializer, VideoTagSerializer)


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Allow read to anyone, write only to authenticated users."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == getattr(
            obj, "uploader", None
        ) or request.user == getattr(obj, "user", None)


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve videos."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return VideoDetailSerializer
        return VideoListSerializer

    def get_queryset(self):
        qs = (
            Video.objects.select_related("uploader", "channel")
            .defer("video_file", "description")
            .order_by("-uploaded_at")
        )
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__tag__name__iexact=tag)
        search = self.request.query_params.get("search")
        if search:
            from django.db.models import Q

            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return qs

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        video = self.get_object()
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reaction = serializer.validated_data["reaction"]
        obj, created = VideoReaction.objects.get_or_create(
            user=request.user, video=video, defaults={"reaction": reaction}
        )
        if not created:
            if obj.reaction == reaction:
                obj.delete()
                return Response({"reaction": None})
            else:
                obj.reaction = reaction
                obj.save()
        return Response({"reaction": obj.reaction})

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        video = self.get_object()
        comments = video.comments.select_related("user").order_by("-created_at")
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        video = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data, context={"request": request, "video": video}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_to_playlist(self, request, pk=None):
        """Add or remove video from user's playlists."""
        video = self.get_object()
        serializer = AddToPlaylistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        playlist_ids = serializer.validated_data["playlist_ids"]
        action_type = serializer.validated_data["action"]

        # Validate ownership of all playlist IDs
        user_playlist_ids = set(
            Playlist.objects.filter(owner=request.user).values_list("pk", flat=True)
        )
        valid_ids = set(playlist_ids) & user_playlist_ids

        if action_type == "add":
            for pl_id in valid_ids:
                PlaylistItem.objects.get_or_create(
                    playlist_id=pl_id,
                    video=video,
                )
            return Response({"added_to": list(valid_ids)})
        else:
            deleted, _ = PlaylistItem.objects.filter(
                playlist__owner=request.user,
                video=video,
                playlist__pk__in=valid_ids,
            ).delete()
            return Response({"removed_from": list(valid_ids)})


class PlaylistViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve playlists."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PlaylistSerializer
    lookup_field = "pk"

    def get_queryset(self):
        qs = Playlist.objects.select_related("owner").order_by("-updated_at")
        if self.request.user.is_authenticated:
            # Public playlists + user's own
            return qs.filter(
                models.Q(visibility="public") | models.Q(owner=self.request.user)
            )
        return qs.filter(visibility="public")


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve channels."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Channel.objects.select_related("owner").order_by("-created_at")
    serializer_class = ChannelSerializer
    lookup_field = "pk"


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """List all tags."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = VideoTag.objects.all().order_by("name")
    serializer_class = VideoTagSerializer
    pagination_class = None


class MeView(APIView):
    """Current user profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
