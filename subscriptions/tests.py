from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Subscription

User = get_user_model()


class SubscriptionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sub_user', email='subuser@test.com', password='pass')
        self.channel_user = User.objects.create_user(
            username='channel', email='channel@test.com', password='pass'
        )

    def test_create_subscription(self):
        sub = Subscription.objects.create(
            user=self.user, channel=self.channel_user
        )
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(str(sub), f"{self.user} subscribed to {self.channel_user}")

    def test_prevent_self_subscription(self):
        with self.assertRaises(ValidationError):
            sub = Subscription(user=self.user, channel=self.user)
            sub.full_clean()

    def test_prevent_self_subscription_via_save(self):
        with self.assertRaises(ValidationError):
            Subscription.objects.create(user=self.user, channel=self.user)

    def test_unique_subscription_constraint(self):
        Subscription.objects.create(user=self.user, channel=self.channel_user)
        with self.assertRaises(Exception):
            Subscription.objects.create(
                user=self.user, channel=self.channel_user
            )


class SubscriptionListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='list_user', email='listuser@test.com', password='pass')
        self.channel_user = User.objects.create_user(
            username='list_channel', email='listchannel@test.com', password='pass'
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('subscription_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_subscriptions(self):
        Subscription.objects.create(
            user=self.user, channel=self.channel_user
        )
        self.client.login(username='list_user', password='pass')
        response = self.client.get(reverse('subscription_list'))
        self.assertContains(response, 'list_channel')

    def test_list_empty_for_no_subscriptions(self):
        self.client.login(username='list_user', password='pass')
        response = self.client.get(reverse('subscription_list'))
        self.assertEqual(response.status_code, 200)


class ToggleSubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='toggle_user', email='toggleuser@test.com', password='pass')
        self.channel_user = User.objects.create_user(
            username='toggle_channel', email='togglechannel@test.com', password='pass'
        )

    def test_toggle_requires_login(self):
        response = self.client.post(
            reverse('toggle_subscription', args=[self.channel_user.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_subscribe(self):
        self.client.login(username='toggle_user', password='pass')
        self.client.post(
            reverse('toggle_subscription', args=[self.channel_user.pk])
        )
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, channel=self.channel_user
            ).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(
            user=self.user, channel=self.channel_user
        )
        self.client.login(username='toggle_user', password='pass')
        self.client.post(
            reverse('toggle_subscription', args=[self.channel_user.pk])
        )
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user, channel=self.channel_user
            ).exists()
        )

    def test_self_subscription_redirects(self):
        self.client.login(username='toggle_user', password='pass')
        response = self.client.post(
            reverse('toggle_subscription', args=[self.user.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_subscription_update_channel_list(self):
        self.client.login(username='toggle_user', password='pass')
        self.client.post(
            reverse('toggle_subscription', args=[self.channel_user.pk])
        )
        response = self.client.get(reverse('subscription_list'))
        self.assertContains(response, 'toggle_channel')
