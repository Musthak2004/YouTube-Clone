from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Channel

User = get_user_model()


class ChannelListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='channeller', email='ch@test.com', password='pass'
        )

    def test_channel_list_status_code(self):
        response = self.client.get(reverse('channel_list'))
        self.assertEqual(response.status_code, 200)

    def test_channel_list_uses_correct_template(self):
        response = self.client.get(reverse('channel_list'))
        self.assertTemplateUsed(response, 'channels/channel_list.html')

    def test_channel_list_shows_channels(self):
        response = self.client.get(reverse('channel_list'))
        self.assertContains(response, 'channeller')
        self.assertContains(response, 'Channel')

    def test_channel_list_empty_state(self):
        user2 = User.objects.create_user(
            username='lonely', email='lonely@test.com', password='pass'
        )
        # Delete the auto-created channel
        Channel.objects.filter(owner=user2).delete()
        Channel.objects.filter(owner=self.user).delete()
        response = self.client.get(reverse('channel_list'))
        self.assertContains(response, 'No channels yet')

    def test_channel_list_pagination(self):
        User.objects.create_user(
            username='u1', email='u1@test.com', password='pass'
        )
        User.objects.create_user(
            username='u2', email='u2@test.com', password='pass'
        )
        User.objects.create_user(
            username='u3', email='u3@test.com', password='pass'
        )
        response = self.client.get(reverse('channel_list'))
        self.assertEqual(response.status_code, 200)


class ChannelDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='detail_user', email='det@test.com', password='pass'
        )
        self.channel = Channel.objects.get(owner=self.user)

    def test_channel_detail_status_code(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_channel_detail_uses_correct_template(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertTemplateUsed(response, 'channels/channel_detail.html')

    def test_channel_detail_shows_name(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertContains(response, 'detail_user')
        self.assertContains(response, 'Channel')

    def test_channel_detail_shows_subscriber_count(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertContains(response, '0 subscriber')

    def test_channel_detail_shows_video_count(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertContains(response, '0 video')

    def test_channel_detail_404(self):
        response = self.client.get(
            reverse('channel_detail', args=[9999])
        )
        self.assertEqual(response.status_code, 404)

    def test_channel_detail_context_has_extra(self):
        response = self.client.get(
            reverse('channel_detail', args=[self.channel.pk])
        )
        self.assertIn('subscriber_count', response.context)
        self.assertIn('video_count', response.context)
        self.assertIn('total_views', response.context)
        self.assertIn('is_subscribed', response.context)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class ChannelCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator', email='creator@test.com', password='pass'
        )
        # Delete the auto-created channel to test create view
        Channel.objects.filter(owner=self.user).delete()

    def test_create_requires_login(self):
        response = self.client.get(reverse('channel_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_page_status_code(self):
        self.client.login(username='creator', password='pass')
        response = self.client.get(reverse('channel_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_page_uses_correct_template(self):
        self.client.login(username='creator', password='pass')
        response = self.client.get(reverse('channel_create'))
        self.assertTemplateUsed(response, 'channels/channel_create.html')

    def test_create_channel(self):
        self.client.login(username='creator', password='pass')
        response = self.client.post(reverse('channel_create'), {
            'name': 'My New Channel',
            'description': 'A cool channel',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Channel.objects.filter(name='My New Channel').exists()
        )

    def test_create_channel_sets_owner(self):
        self.client.login(username='creator', password='pass')
        self.client.post(reverse('channel_create'), {
            'name': 'Owner Test Channel',
        })
        channel = Channel.objects.get(name='Owner Test Channel')
        self.assertEqual(channel.owner, self.user)


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class ChannelUpdateTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='ch_owner', email='chown@test.com', password='pass'
        )
        self.other = User.objects.create_user(
            username='ch_other', email='chother@test.com', password='pass'
        )
        self.channel = Channel.objects.get(owner=self.owner)

    def test_update_requires_login(self):
        response = self.client.get(
            reverse('channel_update', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_update_allows_owner(self):
        self.client.login(username='ch_owner', password='pass')
        response = self.client.get(
            reverse('channel_update', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_update_denies_non_owner(self):
        self.client.login(username='ch_other', password='pass')
        response = self.client.get(
            reverse('channel_update', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_update_channel(self):
        self.client.login(username='ch_owner', password='pass')
        response = self.client.post(
            reverse('channel_update', args=[self.channel.pk]),
            {'name': 'Updated Name', 'description': 'Updated desc'}
        )
        self.assertEqual(response.status_code, 302)
        self.channel.refresh_from_db()
        self.assertEqual(self.channel.name, 'Updated Name')
        self.assertEqual(self.channel.description, 'Updated desc')


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class ChannelDeleteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='del_owner', email='delown@test.com', password='pass'
        )
        self.other = User.objects.create_user(
            username='del_other', email='delother@test.com', password='pass'
        )
        self.channel = Channel.objects.get(owner=self.owner)

    def test_delete_requires_login(self):
        response = self.client.get(
            reverse('channel_delete', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_page_status_code(self):
        self.client.login(username='del_owner', password='pass')
        response = self.client.get(
            reverse('channel_delete', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_denies_non_owner(self):
        self.client.login(username='del_other', password='pass')
        response = self.client.post(
            reverse('channel_delete', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Channel.objects.filter(pk=self.channel.pk).exists())

    def test_delete_channel(self):
        self.client.login(username='del_owner', password='pass')
        response = self.client.post(
            reverse('channel_delete', args=[self.channel.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Channel.objects.filter(pk=self.channel.pk).exists())

    def test_delete_redirects_to_channel_list(self):
        self.client.login(username='del_owner', password='pass')
        response = self.client.post(
            reverse('channel_delete', args=[self.channel.pk])
        )
        self.assertRedirects(response, reverse('channel_list'))
