from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from videos.models import Video, VideoReaction
from channels.models import Channel
from comments.models import Comment
from recommendations.models import VideoTag
from .serializers import (
    VideoListSerializer, VideoDetailSerializer,
    ChannelSerializer, CommentSerializer, CommentCreateSerializer,
    ReactionSerializer, UserSerializer, VideoTagSerializer,
)


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Allow read to anyone, write only to authenticated users."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == getattr(obj, 'uploader', None) or \
               request.user == getattr(obj, 'user', None)


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve videos."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VideoDetailSerializer
        return VideoListSerializer

    def get_queryset(self):
        qs = Video.objects.select_related('uploader', 'channel').defer(
            'video_file', 'description'
        ).order_by('-uploaded_at')
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__tag__name__iexact=tag)
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        return qs

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        video = self.get_object()
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reaction = serializer.validated_data['reaction']
        obj, created = VideoReaction.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'reaction': reaction}
        )
        if not created:
            if obj.reaction == reaction:
                obj.delete()
                return Response({'reaction': None})
            else:
                obj.reaction = reaction
                obj.save()
        return Response({'reaction': obj.reaction})

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        video = self.get_object()
        comments = video.comments.select_related('user').order_by('-created_at')
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        video = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request, 'video': video}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve channels."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Channel.objects.select_related('owner').order_by('-created_at')
    serializer_class = ChannelSerializer
    lookup_field = 'pk'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """List all tags."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = VideoTag.objects.all().order_by('name')
    serializer_class = VideoTagSerializer
    pagination_class = None


class MeView(APIView):
    """Current user profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
