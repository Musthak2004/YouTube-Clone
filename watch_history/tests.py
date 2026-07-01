from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from videos.models import Video
from .models import WatchHistory

User = get_user_model()


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class WatchHistoryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='history_user', email='hist@test.com', password='pass'
        )
        self.uploader = User.objects.create_user(
            username='vid_uploader', email='vupload@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.uploader, title='Watched Video'
        )
        WatchHistory.objects.create(
            user=self.user, video=self.video, watch_duration=30
        )

    def test_history_requires_login(self):
        response = self.client.get(reverse('watch_history'))
        self.assertEqual(response.status_code, 302)

    def test_history_status_code(self):
        self.client.login(username='history_user', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertEqual(response.status_code, 200)

    def test_history_uses_correct_template(self):
        self.client.login(username='history_user', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertTemplateUsed(response, 'watch_history/watch_history.html')

    def test_history_shows_watched_video(self):
        self.client.login(username='history_user', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertContains(response, 'Watched Video')

    def test_history_shows_total_count(self):
        self.client.login(username='history_user', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertEqual(response.context['total_count'], 1)

    def test_history_empty(self):
        other_user = User.objects.create_user(
            username='other_hist', email='o-hist@test.com', password='pass'
        )
        self.client.login(username='other_hist', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertContains(response, 'No watch history')

    def test_history_only_shows_own(self):
        self.client.login(username='history_user', password='pass')
        response = self.client.get(reverse('watch_history'))
        self.assertEqual(len(response.context['history']), 1)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class ClearWatchHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='clear_user', email='clearwh@test.com', password='pass'
        )
        self.uploader = User.objects.create_user(
            username='vid_up', email='vidup@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.uploader, title='Video'
        )
        WatchHistory.objects.create(
            user=self.user, video=self.video, watch_duration=10
        )

    def test_clear_history_requires_login(self):
        response = self.client.post(reverse('watch_history_clear'))
        self.assertEqual(response.status_code, 302)

    def test_clear_history(self):
        self.client.login(username='clear_user', password='pass')
        self.client.post(reverse('watch_history_clear'))
        self.assertEqual(
            WatchHistory.objects.filter(user=self.user).count(), 0
        )

    def test_clear_history_redirects(self):
        self.client.login(username='clear_user', password='pass')
        response = self.client.post(reverse('watch_history_clear'))
        self.assertRedirects(response, reverse('watch_history'))

    def test_clear_only_clears_own_history(self):
        other_user = User.objects.create_user(
            username='other_clear', email='oclear@test.com', password='pass'
        )
        other_video = Video.objects.create(
            uploader=other_user, title='Other Video'
        )
        WatchHistory.objects.create(
            user=other_user, video=other_video, watch_duration=5
        )
        self.client.login(username='clear_user', password='pass')
        self.client.post(reverse('watch_history_clear'))
        self.assertEqual(
            WatchHistory.objects.filter(user=other_user).count(), 1
        )


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class RemoveWatchHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='remove_user', email='rmwh@test.com', password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other_rm', email='orm@test.com', password='pass'
        )
        self.uploader = User.objects.create_user(
            username='vid_rm', email='vidrm@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.uploader, title='Remove Me'
        )
        self.history = WatchHistory.objects.create(
            user=self.user, video=self.video, watch_duration=20
        )

    def test_remove_requires_login(self):
        response = self.client.post(
            reverse('watch_history_remove', args=[self.history.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_remove_entry(self):
        self.client.login(username='remove_user', password='pass')
        self.client.post(
            reverse('watch_history_remove', args=[self.history.pk])
        )
        self.assertFalse(
            WatchHistory.objects.filter(pk=self.history.pk).exists()
        )

    def test_cannot_remove_others_entry(self):
        other_history = WatchHistory.objects.create(
            user=self.other_user,
            video=self.video,
            watch_duration=15,
        )
        self.client.login(username='remove_user', password='pass')
        self.client.post(
            reverse('watch_history_remove', args=[other_history.pk])
        )
        self.assertTrue(
            WatchHistory.objects.filter(pk=other_history.pk).exists()
        )

    def test_remove_redirects(self):
        self.client.login(username='remove_user', password='pass')
        response = self.client.post(
            reverse('watch_history_remove', args=[self.history.pk])
        )
        self.assertEqual(response.status_code, 302)
