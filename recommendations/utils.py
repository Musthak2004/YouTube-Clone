from django.db.models import Count, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta
from videos.models import Video
from .models import VideoTagMap, UserInterest


def get_recommendations(user, count=12):
    if not user.is_authenticated:
        return Video.objects.none()

    top_tags = UserInterest.objects.filter(
        user=user, score__gt=0
    ).select_related('tag').order_by('-score')[:5]

    if not top_tags.exists():
        return Video.objects.none()

    tag_ids = [ut.tag_id for ut in top_tags]

    watched_video_ids = list(
        user.watch_history.values_list('video_id', flat=True)
    )

    matched = VideoTagMap.objects.filter(
        tag_id__in=tag_ids
    ).exclude(
        video_id__in=watched_video_ids
    ).values('video_id').annotate(
        tag_match=Count('id')
    ).filter(tag_match__gte=1)

    video_ids = [m['video_id'] for m in matched]

    if not video_ids:
        return Video.objects.none()

    recency_cutoff = timezone.now() - timedelta(days=14)

    videos = Video.objects.filter(pk__in=video_ids).annotate(
        recency_bonus=Case(
            When(uploaded_at__gte=recency_cutoff, then=2),
            default=0,
            output_field=IntegerField()
        ),
        tag_score=Count('tags__id')
    ).order_by('-tag_score', '-views', '-uploaded_at')[:count]

    return videos
