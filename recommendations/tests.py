from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from videos.models import Video
from .models import VideoTag, VideoTagMap, UserInterest

User = get_user_model()


class VideoTagModelTests(TestCase):
    def test_create_tag(self):
        tag = VideoTag.objects.create(name='python')
        self.assertEqual(str(tag), 'python')

    def test_tag_name_unique(self):
        VideoTag.objects.create(name='unique_tag')
        with self.assertRaises(IntegrityError):
            VideoTag.objects.create(name='unique_tag')

    def test_tag_ordering(self):
        VideoTag.objects.create(name='zebra')
        VideoTag.objects.create(name='apple')
        tags = VideoTag.objects.all()
        self.assertEqual(tags[0].name, 'apple')
        self.assertEqual(tags[1].name, 'zebra')


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoTagMapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tagmap_user', email='tagmap@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.user, title='Tagged Video'
        )
        self.tag = VideoTag.objects.create(name='tutorial')

    def test_create_tag_map(self):
        mapping = VideoTagMap.objects.create(
            video=self.video, tag=self.tag
        )
        self.assertEqual(
            str(mapping), f'{self.video.title} → {self.tag.name}'
        )

    def test_unique_video_tag(self):
        VideoTagMap.objects.create(video=self.video, tag=self.tag)
        with self.assertRaises(IntegrityError):
            VideoTagMap.objects.create(video=self.video, tag=self.tag)

    def test_video_related_name(self):
        VideoTagMap.objects.create(video=self.video, tag=self.tag)
        self.assertEqual(self.video.tags.count(), 1)

    def test_tag_related_name(self):
        VideoTagMap.objects.create(video=self.video, tag=self.tag)
        self.assertEqual(self.tag.videos.count(), 1)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class UserInterestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='interest_user', email='interest@test.com', password='pass'
        )
        self.tag = VideoTag.objects.create(name='gaming')

    def test_create_interest(self):
        interest = UserInterest.objects.create(
            user=self.user, tag=self.tag, score=1
        )
        self.assertEqual(
            str(interest), f'{self.user.username} → {self.tag.name} (1)'
        )

    def test_unique_user_tag_interest(self):
        UserInterest.objects.create(user=self.user, tag=self.tag)
        with self.assertRaises(IntegrityError):
            UserInterest.objects.create(user=self.user, tag=self.tag)

    def test_score_defaults_to_zero(self):
        interest = UserInterest.objects.create(
            user=self.user, tag=self.tag
        )
        self.assertEqual(interest.score, 0)

    def test_score_increment(self):
        interest = UserInterest.objects.create(
            user=self.user, tag=self.tag, score=1
        )
        interest.score += 1
        interest.save()
        self.assertEqual(
            UserInterest.objects.get(user=self.user, tag=self.tag).score, 2
        )


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class TagVideoListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tag_viewer', email='tagview@test.com', password='pass'
        )
        self.uploader = User.objects.create_user(
            username='vid_uploader', email='vidup@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.uploader, title='Django Basics'
        )
        self.tag = VideoTag.objects.create(name='django')
        self.other_tag = VideoTag.objects.create(name='python')
        VideoTagMap.objects.create(video=self.video, tag=self.tag)

    def test_tag_video_list_status_code(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.tag.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_tag_video_list_uses_correct_template(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.tag.pk])
        )
        self.assertTemplateUsed(response, 'recommendations/tag_videos.html')

    def test_tag_video_list_shows_videos(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.tag.pk])
        )
        self.assertContains(response, 'Django Basics')
        self.assertContains(response, '#django')

    def test_tag_video_list_no_videos(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.other_tag.pk])
        )
        self.assertContains(response, 'No videos yet')

    def test_tag_video_list_404(self):
        response = self.client.get(
            reverse('tag_videos', args=[9999])
        )
        self.assertEqual(response.status_code, 404)

    def test_tag_in_context(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.tag.pk])
        )
        self.assertEqual(response.context['tag'], self.tag)

    def test_all_tags_in_context(self):
        response = self.client.get(
            reverse('tag_videos', args=[self.tag.pk])
        )
        self.assertIn(self.tag, response.context['all_tags'])
        self.assertIn(self.other_tag, response.context['all_tags'])

    def test_interest_incremented_when_authenticated(self):
        self.client.login(username='tag_viewer', password='pass')
        self.client.get(reverse('tag_videos', args=[self.tag.pk]))
        interest = UserInterest.objects.get(
            user=self.user, tag=self.tag
        )
        self.assertEqual(interest.score, 1)

    def test_interest_not_created_when_anonymous(self):
        self.client.get(reverse('tag_videos', args=[self.tag.pk]))
        self.assertEqual(
            UserInterest.objects.filter(tag=self.tag).count(), 0
        )

    def test_interest_increments_multiple_visits(self):
        self.client.login(username='tag_viewer', password='pass')
        self.client.get(reverse('tag_videos', args=[self.tag.pk]))
        self.client.get(reverse('tag_videos', args=[self.tag.pk]))
        interest = UserInterest.objects.get(
            user=self.user, tag=self.tag
        )
        self.assertEqual(interest.score, 2)
