from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from subscriptions.models import Subscription
from videos.models import Video

from .models import Notification

User = get_user_model()


def make_user(username, password="pass", **kwargs):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com", password=password, **kwargs
    )


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class NotificationModelTests(TestCase):
    def test_create_notification(self):
        user1 = make_user("alice")
        user2 = make_user("bob")
        n = Notification.objects.create(
            recipient=user1,
            actor=user2,
            verb="subscribed",
        )
        self.assertEqual(str(n), "bob subscribed — alice")
        self.assertFalse(n.is_read)
        self.assertIsNotNone(n.created_at)

    def test_notification_ordering(self):
        user1 = make_user("alice")
        user2 = make_user("bob")
        n1 = Notification.objects.create(
            recipient=user1, actor=user2, verb="subscribed"
        )
        n2 = Notification.objects.create(recipient=user1, actor=user2, verb="commented")
        qs = Notification.objects.all()
        self.assertEqual(qs.first(), n2)
        self.assertEqual(qs.last(), n1)

    def test_notification_with_video(self):
        uploader = make_user("uploader")
        viewer = make_user("viewer")
        video = Video.objects.create(
            uploader=uploader, title="Test Video", description="Test"
        )
        n = Notification.objects.create(
            recipient=uploader,
            actor=viewer,
            verb="liked",
            target_video=video,
        )
        self.assertEqual(n.target_video, video)
        self.assertEqual(n.target_video.title, "Test Video")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class NotificationSignalTests(TestCase):
    def test_comment_creates_notification(self):
        uploader = make_user("uploader")
        commenter = make_user("commenter")
        video = Video.objects.create(
            uploader=uploader, title="My Video", description="Desc"
        )
        self.client.login(username="commenter", password="pass")
        self.client.post(
            reverse("comment_create", args=[video.pk]),
            {"text": "Great video!"},
        )
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.actor, commenter)
        self.assertEqual(n.recipient, uploader)
        self.assertEqual(n.verb, "commented")
        self.assertEqual(n.target_video, video)

    def test_comment_self_notification_not_created(self):
        uploader = make_user("uploader")
        video = Video.objects.create(
            uploader=uploader, title="My Video", description="Desc"
        )
        self.client.login(username="uploader", password="pass")
        self.client.post(
            reverse("comment_create", args=[video.pk]),
            {"text": "My own video!"},
        )
        self.assertEqual(Notification.objects.count(), 0)

    def test_subscribe_creates_notification(self):
        alice = make_user("alice")
        bob = make_user("bob")
        self.client.login(username="bob", password="pass")
        self.client.post(
            reverse("toggle_subscription", args=[alice.pk]),
        )
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.actor, bob)
        self.assertEqual(n.recipient, alice)
        self.assertEqual(n.verb, "subscribed")

    def test_subscribe_self_notification_not_created(self):
        alice = make_user("alice")
        self.client.login(username="alice", password="pass")
        # Subscription model's clean() prevents self-sub, so create directly
        with self.assertRaises(Exception):
            Subscription.objects.create(user=alice, channel=alice)
        self.assertEqual(Notification.objects.count(), 0)

    def test_like_creates_notification(self):
        uploader = make_user("uploader")
        liker = make_user("liker")
        video = Video.objects.create(
            uploader=uploader, title="Nice Vid", description="Desc"
        )
        self.client.login(username="liker", password="pass")
        self.client.post(
            reverse("video_reaction", args=[video.pk]),
            {"reaction": "like"},
        )
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.actor, liker)
        self.assertEqual(n.recipient, uploader)
        self.assertEqual(n.verb, "liked")
        self.assertEqual(n.target_video, video)

    def test_like_self_notification_not_created(self):
        uploader = make_user("uploader")
        video = Video.objects.create(
            uploader=uploader, title="My Video", description="Desc"
        )
        self.client.login(username="uploader", password="pass")
        self.client.post(
            reverse("video_reaction", args=[video.pk]),
            {"reaction": "like"},
        )
        self.assertEqual(Notification.objects.count(), 0)

    def test_like_no_duplicate_notifications(self):
        uploader = make_user("uploader")
        liker = make_user("liker")
        video = Video.objects.create(
            uploader=uploader, title="Nice Vid", description="Desc"
        )
        # Create first like notification directly
        Notification.objects.create(
            recipient=uploader, actor=liker, verb="liked", target_video=video
        )
        # Like again via reaction (should not create duplicate)
        self.client.login(username="liker", password="pass")
        self.client.post(
            reverse("video_reaction", args=[video.pk]),
            {"reaction": "like"},
        )
        self.assertEqual(Notification.objects.count(), 1)

    def test_dislike_does_not_create_notification(self):
        uploader = make_user("uploader")
        make_user("disliker")
        video = Video.objects.create(uploader=uploader, title="Meh", description="Desc")
        self.client.login(username="disliker", password="pass")
        self.client.post(
            reverse("video_reaction", args=[video.pk]),
            {"reaction": "dislike"},
        )
        self.assertEqual(Notification.objects.count(), 0)

    def test_upload_notifies_subscribers(self):
        uploader = make_user("uploader")
        subscriber = make_user("subscriber")
        # Subscribe to uploader — this creates a subscribe notification,
        # so clear notifications before testing the upload signal
        Subscription.objects.create(user=subscriber, channel=uploader)
        Notification.objects.all().delete()

        # Upload a video
        self.client.login(username="uploader", password="pass")
        self.client.post(
            reverse("video_create"),
            {"title": "New Upload!", "description": "Check it out"},
        )
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.actor, uploader)
        self.assertEqual(n.recipient, subscriber)
        self.assertEqual(n.verb, "uploaded")

    def test_upload_does_not_notify_self(self):
        make_user("uploader")
        # Subscribe to self (not possible via clean(), so verify it doesn't happen)
        self.client.login(username="uploader", password="pass")
        self.client.post(
            reverse("video_create"),
            {"title": "My Upload", "description": "Desc"},
        )
        self.assertEqual(Notification.objects.count(), 0)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class NotificationViewTests(TestCase):
    def setUp(self):
        self.user = make_user("alice")
        self.other = make_user("bob")
        self.client.login(username="alice", password="pass")

        # Create a few notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                actor=self.other,
                verb="commented" if i % 2 == 0 else "subscribed",
            )

    def test_list_view_status_code(self):
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_uses_correct_template(self):
        response = self.client.get(reverse("notification_list"))
        self.assertTemplateUsed(response, "notifications/notification_list.html")

    def test_list_view_shows_notifications(self):
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(len(response.context["notifications"]), 3)
        self.assertEqual(response.context["total_count"], 3)
        self.assertEqual(response.context["unread_count"], 3)

    def test_list_view_shows_read_count(self):
        # Mark one as read
        n = Notification.objects.first()
        n.is_read = True
        n.save()
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(response.context["unread_count"], 2)
        self.assertEqual(response.context["total_count"], 3)

    def test_list_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(response.status_code, 302)

    def test_mark_as_read(self):
        n = Notification.objects.first()
        self.assertFalse(n.is_read)
        response = self.client.post(
            reverse("mark_as_read", args=[n.pk]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_as_read_only_own_notification(self):
        # other user's notification
        n = Notification.objects.create(
            recipient=self.other,
            actor=self.user,
            verb="subscribed",
        )
        response = self.client.post(
            reverse("mark_as_read", args=[n.pk]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        n.refresh_from_db()
        self.assertFalse(n.is_read)

    def test_mark_all_as_read(self):
        response = self.client.post(reverse("mark_all_read"))
        self.assertRedirects(response, reverse("notification_list"))
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=False).count(),
            0,
        )

    def test_mark_all_as_read_only_own(self):
        # Create notification for other user
        Notification.objects.create(
            recipient=self.other,
            actor=self.user,
            verb="subscribed",
        )
        self.client.post(reverse("mark_all_read"))
        # Other user's notification should still be unread
        other_unread = Notification.objects.filter(
            recipient=self.other, is_read=False
        ).count()
        self.assertEqual(other_unread, 1)

    def test_mark_all_as_read_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("mark_all_read"))
        self.assertEqual(response.status_code, 302)

    def test_unread_count(self):
        response = self.client.get(reverse("unread_count"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"count": 3})

    def test_unread_count_after_read(self):
        n = Notification.objects.first()
        n.is_read = True
        n.save()
        response = self.client.get(reverse("unread_count"))
        self.assertJSONEqual(response.content, {"count": 2})

    def test_empty_state(self):
        Notification.objects.filter(recipient=self.user).delete()
        response = self.client.get(reverse("notification_list"))
        self.assertContains(response, "All caught up")
        self.assertEqual(len(response.context["notifications"]), 0)

    def test_list_pagination(self):
        # Create more notifications to test pagination
        for i in range(25):
            Notification.objects.create(
                recipient=self.user,
                actor=self.other,
                verb="commented",
            )
        response = self.client.get(reverse("notification_list"))
        self.assertEqual(len(response.context["notifications"]), 20)
        self.assertTrue(response.context["is_paginated"])

    def test_list_page_2(self):
        for i in range(25):
            Notification.objects.create(
                recipient=self.user,
                actor=self.other,
                verb="commented",
            )
        response = self.client.get(reverse("notification_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["notifications"]), 8)
