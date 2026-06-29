from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Video, VideoReaction, VideoView

User = get_user_model()


def make_user(username, password='pass', **kwargs):
    return User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password=password,
        **kwargs
    )


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoListTests(TestCase):
    def test_video_list_status_code(self):
        response = self.client.get(reverse('video_list'))
        self.assertEqual(response.status_code, 200)

    def test_video_list_uses_correct_template(self):
        response = self.client.get(reverse('video_list'))
        self.assertTemplateUsed(response, 'videos/video_list.html')

    def test_video_list_shows_videos(self):
        user = make_user('uploader')
        Video.objects.create(
            uploader=user,
            title='Test Video',
            description='A test video',
        )
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, 'Test Video')

    def test_video_list_shows_empty_state(self):
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, 'No videos yet')


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoCreateTests(TestCase):
    def setUp(self):
        self.user = make_user('uploader')
        self.client.login(username='uploader', password='pass')

    def test_create_page_status_code(self):
        response = self.client.get(reverse('video_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('video_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_video(self):
        video_file = SimpleUploadedFile(
            'test.mp4', b'file_content', content_type='video/mp4'
        )
        response = self.client.post(reverse('video_create'), {
            'title': 'New Video',
            'description': 'A new video',
            'video_file': video_file,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Video.objects.filter(title='New Video').exists())

    def test_create_video_sets_uploader(self):
        video_file = SimpleUploadedFile(
            'test.mp4', b'file_content', content_type='video/mp4'
        )
        self.client.post(reverse('video_create'), {
            'title': 'My Upload',
            'description': 'test',
            'video_file': video_file,
        })
        video = Video.objects.get(title='My Upload')
        self.assertEqual(video.uploader, self.user)

    def test_create_video_links_channel(self):
        video_file = SimpleUploadedFile(
            'test.mp4', b'file_content', content_type='video/mp4'
        )
        self.client.post(reverse('video_create'), {
            'title': 'Channel Video',
            'description': 'test',
            'video_file': video_file,
        })
        video = Video.objects.get(title='Channel Video')
        self.assertIsNotNone(video.channel)
        self.assertEqual(video.channel.owner, self.user)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoDetailTests(TestCase):
    def setUp(self):
        self.user = make_user('uploader')
        self.video = Video.objects.create(
            uploader=self.user, title='Test Video', description='A test video'
        )

    def test_detail_page_status_code(self):
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_uses_correct_template(self):
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertTemplateUsed(response, 'videos/video_detail.html')

    def test_detail_page_shows_title(self):
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertContains(response, 'Test Video')

    def test_detail_page_tracks_view(self):
        self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertEqual(VideoView.objects.count(), 1)
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, 1)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoReactionTests(TestCase):
    def setUp(self):
        self.user = make_user('viewer')
        self.uploader = make_user('uploader')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )
        self.client.login(username='viewer', password='pass')

    def test_like_video(self):
        response = self.client.post(
            reverse('video_reaction', args=[self.video.pk]),
            {'reaction': 'like'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            VideoReaction.objects.filter(
                user=self.user, video=self.video, reaction='like'
            ).exists()
        )

    def test_dislike_video(self):
        self.client.post(
            reverse('video_reaction', args=[self.video.pk]),
            {'reaction': 'dislike'}
        )
        self.assertTrue(
            VideoReaction.objects.filter(
                user=self.user, video=self.video, reaction='dislike'
            ).exists()
        )

    def test_toggle_like_off(self):
        VideoReaction.objects.create(
            user=self.user, video=self.video, reaction='like'
        )
        self.client.post(
            reverse('video_reaction', args=[self.video.pk]),
            {'reaction': 'like'}
        )
        self.assertEqual(
            VideoReaction.objects.filter(
                user=self.user, video=self.video
            ).count(),
            0
        )

    def test_switch_from_like_to_dislike(self):
        VideoReaction.objects.create(
            user=self.user, video=self.video, reaction='like'
        )
        self.client.post(
            reverse('video_reaction', args=[self.video.pk]),
            {'reaction': 'dislike'}
        )
        reaction = VideoReaction.objects.get(user=self.user, video=self.video)
        self.assertEqual(reaction.reaction, 'dislike')

    def test_reaction_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertEqual(response.status_code, 200)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class VideoUpdateDeleteTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.video = Video.objects.create(
            uploader=self.owner, title='Original Title'
        )

    def test_update_requires_login(self):
        response = self.client.get(reverse('video_update', args=[self.video.pk]))
        self.assertEqual(response.status_code, 302)

    def test_update_allows_owner(self):
        self.client.login(username='owner', password='pass')
        video_file = SimpleUploadedFile(
            'updated.mp4', b'new_content', content_type='video/mp4'
        )
        response = self.client.post(
            reverse('video_update', args=[self.video.pk]),
            {'title': 'Updated Title', 'description': 'updated', 'video_file': video_file}
        )
        self.assertEqual(response.status_code, 302)
        self.video.refresh_from_db()
        self.assertEqual(self.video.title, 'Updated Title')

    def test_update_denies_non_owner(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('video_update', args=[self.video.pk]))
        self.assertEqual(response.status_code, 403)

    def test_delete_requires_login(self):
        response = self.client.get(reverse('video_delete', args=[self.video.pk]))
        self.assertEqual(response.status_code, 302)

    def test_delete_allows_owner(self):
        self.client.login(username='owner', password='pass')
        response = self.client.post(reverse('video_delete', args=[self.video.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Video.objects.filter(pk=self.video.pk).exists())

    def test_delete_denies_non_owner(self):
        self.client.login(username='other', password='pass')
        response = self.client.post(reverse('video_delete', args=[self.video.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Video.objects.filter(pk=self.video.pk).exists())


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class LikedVideosTests(TestCase):
    def setUp(self):
        self.user = make_user('viewer')
        self.uploader = make_user('uploader2')
        self.video = Video.objects.create(uploader=self.uploader, title='Liked Video')
        VideoReaction.objects.create(
            user=self.user, video=self.video, reaction='like'
        )

    def test_liked_videos_shows_liked(self):
        self.client.login(username='viewer', password='pass')
        response = self.client.get(reverse('liked_videos'))
        self.assertContains(response, 'Liked Video')

    def test_liked_videos_requires_login(self):
        response = self.client.get(reverse('liked_videos'))
        self.assertEqual(response.status_code, 302)

    def test_liked_videos_excludes_not_liked(self):
        other_video = Video.objects.create(uploader=self.uploader, title='Not Liked')
        self.client.login(username='viewer', password='pass')
        response = self.client.get(reverse('liked_videos'))
        self.assertNotContains(response, 'Not Liked')
