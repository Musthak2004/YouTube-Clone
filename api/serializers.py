from rest_framework import serializers
from videos.models import Video, VideoReaction
from channels.models import Channel
from comments.models import Comment
from recommendations.models import VideoTag
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    channel_id = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'bio',
                  'channel_id', 'date_joined']
        read_only_fields = fields

    def get_channel_id(self, obj):
        return getattr(obj, 'channel_id', None)


class ChannelSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    subscriber_count = serializers.SerializerMethodField()
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'owner', 'name', 'description', 'banner',
                  'subscriber_count', 'video_count', 'created_at']

    def get_subscriber_count(self, obj):
        return obj.owner.subscribers_list.count()

    def get_video_count(self, obj):
        return obj.videos.count()


class VideoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTag
        fields = ['id', 'name']


class VideoListSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    channel_name = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'uploader', 'title', 'description', 'thumbnail',
                  'views', 'duration', 'uploaded_at', 'channel_name',
                  'tags', 'like_count', 'dislike_count']

    def get_channel_name(self, obj):
        return obj.channel.name if obj.channel else None

    def get_tags(self, obj):
        return [{'id': tm.tag_id, 'name': tm.tag.name}
                for tm in obj.tags.select_related('tag').all()]

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction='like').count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction='dislike').count()


class VideoDetailSerializer(VideoListSerializer):
    video_url = serializers.URLField(read_only=True)

    class Meta(VideoListSerializer.Meta):
        fields = VideoListSerializer.Meta.fields + ['video_url']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user', 'text', 'created_at', 'updated_at']
        read_only_fields = ['video', 'user', 'created_at', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['video'] = self.context['video']
        return super().create(validated_data)


class ReactionSerializer(serializers.Serializer):
    reaction = serializers.ChoiceField(choices=['like', 'dislike'])
