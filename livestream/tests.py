from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from notifications.models import Notification
from subscriptions.models import Subscription

from .models import ChatMessage, Stream, StreamKey

User = get_user_model()


def make_user(username, password="pass", **kwargs):
    return User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=password,
        **kwargs,
    )


# ---------------------------------------------------------------------------
#  Model Tests
# ---------------------------------------------------------------------------


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class StreamKeyModelTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        # Channel is auto-created via signals.py on user creation
        self.channel = self.user.channel

    def test_stream_key_created_via_signal(self):
        """StreamKey is auto-created when a Channel is created."""
        self.assertTrue(StreamKey.objects.filter(channel=self.channel).exists())

    def test_stream_key_defaults(self):
        key = StreamKey.objects.get(channel=self.channel)
        self.assertIsNotNone(key.key)
        self.assertEqual(len(key.key), 32)  # uuid4().hex is 32 chars
        self.assertTrue(key.is_active)
        self.assertEqual(key.display_name, "")

    def test_stream_key_uniqueness(self):
        """Each channel gets its own key."""
        other_user = make_user("other")
        other_channel = other_user.channel
        first_key = StreamKey.objects.get(channel=self.channel)
        second_key = StreamKey.objects.get(channel=other_channel)
        self.assertNotEqual(first_key.key, second_key.key)

    def test_stream_key_regenerate(self):
        key = StreamKey.objects.get(channel=self.channel)
        old_key = key.key
        key.regenerate()
        self.assertNotEqual(old_key, key.key)
        self.assertEqual(len(key.key), 32)

    def test_stream_key_toggle_active(self):
        key = StreamKey.objects.get(channel=self.channel)
        key.is_active = False
        key.save()
        key.refresh_from_db()
        self.assertFalse(key.is_active)
        key.is_active = True
        key.save()
        key.refresh_from_db()
        self.assertTrue(key.is_active)

    def test_stream_key_str(self):
        key = StreamKey.objects.get(channel=self.channel)
        self.assertIn("StreamKey for", str(key))
        self.assertIn(self.channel.name, str(key))


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class StreamModelTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream_key = StreamKey.objects.get(channel=self.channel)
        self.stream = Stream.objects.create(
            channel=self.channel,
            title="Test Stream",
            description="A test stream",
            stream_key=self.stream_key,
        )

    def test_stream_creation(self):
        self.assertEqual(self.stream.title, "Test Stream")
        self.assertEqual(self.stream.description, "A test stream")
        self.assertEqual(self.stream.channel, self.channel)
        self.assertFalse(self.stream.is_live)
        self.assertEqual(self.stream.viewer_count, 0)

    def test_stream_is_live_flag(self):
        self.assertFalse(self.stream.is_live)
        self.stream.is_live = True
        self.stream.save()
        self.stream.refresh_from_db()
        self.assertTrue(self.stream.is_live)

    def test_stream_get_absolute_url(self):
        url = self.stream.get_absolute_url()
        self.assertEqual(url, reverse("watch_stream", kwargs={"pk": self.stream.pk}))

    def test_stream_str(self):
        self.assertIn("Test Stream", str(self.stream))
        self.assertIn("ended", str(self.stream))
        # Switch to live
        self.stream.is_live = True
        self.stream.save()
        self.stream.refresh_from_db()
        self.assertIn("LIVE", str(self.stream))

    def test_stream_default_ordering(self):
        Stream.objects.create(
            channel=self.channel,
            title="Older Stream",
            started_at=timezone.now() - timezone.timedelta(hours=1),
        )
        qs = Stream.objects.all()
        self.assertEqual(qs.first(), self.stream)

    def test_stream_duration_property(self):
        """Duration is 0 when not started/ended, otherwise difference in seconds."""
        self.assertEqual(self.stream.duration, 0)
        now = timezone.now()
        self.stream.started_at = now - timezone.timedelta(hours=1)
        self.stream.ended_at = now
        self.assertEqual(self.stream.duration, 3600)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ChatMessageModelTests(TestCase):
    def setUp(self):
        self.user = make_user("chatter")
        streamer = make_user("streamer")
        self.channel = streamer.channel
        self.stream = Stream.objects.create(channel=self.channel, title="Stream")

    def test_chat_message_creation(self):
        msg = ChatMessage.objects.create(
            stream=self.stream, user=self.user, message="Hello everyone!"
        )
        self.assertEqual(msg.message, "Hello everyone!")
        self.assertEqual(msg.stream, self.stream)
        self.assertEqual(msg.user, self.user)
        self.assertIsNotNone(msg.sent_at)

    def test_chat_message_ordering(self):
        m1 = ChatMessage.objects.create(
            stream=self.stream, user=self.user, message="First"
        )
        m2 = ChatMessage.objects.create(
            stream=self.stream, user=self.user, message="Second"
        )
        qs = ChatMessage.objects.all()
        self.assertEqual(qs.first(), m1)
        self.assertEqual(qs.last(), m2)

    def test_chat_message_relation(self):
        ChatMessage.objects.create(stream=self.stream, user=self.user, message="Msg 1")
        ChatMessage.objects.create(stream=self.stream, user=self.user, message="Msg 2")
        self.assertEqual(self.stream.chat_messages.count(), 2)

    def test_chat_message_str(self):
        msg = ChatMessage.objects.create(
            stream=self.stream, user=self.user, message="Hello!"
        )
        self.assertIn(self.user.username, str(msg))
        self.assertIn("Hello!", str(msg))

    def test_chat_message_max_length(self):
        """Max_length is enforced by model validation."""
        long_msg = "x" * 501
        msg = ChatMessage(stream=self.stream, user=self.user, message=long_msg)
        with self.assertRaises(Exception):
            msg.full_clean()


# ---------------------------------------------------------------------------
#  View Tests
# ---------------------------------------------------------------------------


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class StreamDashboardViewTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream_key = StreamKey.objects.get(channel=self.channel)
        self.stream = Stream.objects.create(
            channel=self.channel, title="Dashboard Stream"
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("stream_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_status_ok(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertTemplateUsed(response, "livestream/stream_dashboard.html")

    def test_dashboard_shows_user_streams(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertContains(response, "Dashboard Stream")

    def test_dashboard_shows_empty_state(self):
        make_user("emptyuser")
        self.client.login(username="emptyuser", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertContains(response, "No streams")

    def test_dashboard_excludes_other_channels(self):
        other_user = make_user("other")
        Stream.objects.create(channel=other_user.channel, title="Other Stream")
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertNotContains(response, "Other Stream")

    def test_dashboard_context_has_active_stream(self):
        self.client.login(username="streamer", password="pass")
        self.stream.is_live = True
        self.stream.save()
        response = self.client.get(reverse("stream_dashboard"))
        self.assertEqual(response.context["active_stream"], self.stream)

    def test_dashboard_context_has_stream_key(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertTrue(response.context["has_stream_key"])

    def test_dashboard_no_channel_context(self):
        """User whose channel was deleted sees None context values."""
        user_no_channel = make_user("nochan")
        user_no_channel.channel.delete()
        self.client.login(username="nochan", password="pass")
        response = self.client.get(reverse("stream_dashboard"))
        self.assertIsNone(response.context["channel"])
        self.assertIsNone(response.context["active_stream"])
        self.assertFalse(response.context["has_stream_key"])


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class GoLiveViewTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream_key = StreamKey.objects.get(channel=self.channel)

    def test_go_live_requires_login(self):
        response = self.client.get(reverse("go_live"))
        self.assertEqual(response.status_code, 302)

    def test_go_live_get(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("go_live"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "livestream/go_live.html")

    def test_go_live_no_channel_blocked(self):
        no_channel = make_user("nochan")
        no_channel.channel.delete()
        self.client.login(username="nochan", password="pass")
        response = self.client.get(reverse("go_live"))
        self.assertEqual(response.status_code, 403)

    def test_go_live_post_success(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.post(
            reverse("go_live"),
            {
                "title": "My First Stream",
                "description": "Testing live streaming!",
                "stream_key": self.stream_key.key,
            },
        )
        self.assertEqual(response.status_code, 302)
        stream = Stream.objects.get(title="My First Stream")
        self.assertTrue(stream.is_live)
        self.assertIsNotNone(stream.started_at)
        self.assertEqual(stream.channel, self.channel)
        self.assertEqual(stream.stream_key, self.stream_key)

    def test_go_live_invalid_stream_key(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.post(
            reverse("go_live"),
            {
                "title": "Bad Key Stream",
                "stream_key": "invalid-key-12345",
            },
        )
        self.assertEqual(response.status_code, 200)  # Form re-rendered with error
        self.assertFalse(Stream.objects.filter(title="Bad Key Stream").exists())
        self.assertContains(response, "Invalid or inactive")

    def test_go_live_inactive_stream_key(self):
        self.client.login(username="streamer", password="pass")
        self.stream_key.is_active = False
        self.stream_key.save()
        response = self.client.post(
            reverse("go_live"),
            {
                "title": "Inactive Key Stream",
                "stream_key": self.stream_key.key,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Stream.objects.filter(title="Inactive Key Stream").exists())
        self.assertContains(response, "Invalid or inactive")

    def test_go_live_links_channel(self):
        """Stream is linked to the user's channel."""
        self.client.login(username="streamer", password="pass")
        self.client.post(
            reverse("go_live"),
            {
                "title": "Channel Stream",
                "stream_key": self.stream_key.key,
            },
        )
        stream = Stream.objects.get(title="Channel Stream")
        self.assertEqual(stream.channel, self.channel)

    def test_go_live_notifies_subscribers(self):
        """Going live creates 'went_live' notifications."""
        subscriber = make_user("subscriber")
        Subscription.objects.create(user=subscriber, channel=self.user)
        self.client.login(username="streamer", password="pass")
        self.client.post(
            reverse("go_live"),
            {
                "title": "Notifying Stream",
                "stream_key": self.stream_key.key,
            },
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=subscriber,
                actor=self.user,
                verb="went_live",
            ).exists()
        )

    def test_go_live_does_not_notify_self(self):
        """The streamer should not get their own notification."""
        # Use bulk_create to bypass Subscription.full_clean() which blocks self-subs
        Subscription.objects.bulk_create(
            [Subscription(user=self.user, channel=self.user)]
        )
        self.client.login(username="streamer", password="pass")
        self.client.post(
            reverse("go_live"),
            {
                "title": "Self Stream",
                "stream_key": self.stream_key.key,
            },
        )
        self.assertFalse(
            Notification.objects.filter(
                recipient=self.user,
                actor=self.user,
                verb="went_live",
            ).exists()
        )


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class EndStreamViewTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream = Stream.objects.create(
            channel=self.channel,
            title="Ending Stream",
            is_live=True,
            started_at=timezone.now(),
            viewer_count=42,
        )

    def test_end_stream_requires_login(self):
        response = self.client.post(reverse("end_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 302)

    def test_end_stream_owner(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.post(reverse("end_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 302)
        self.stream.refresh_from_db()
        self.assertFalse(self.stream.is_live)
        self.assertIsNotNone(self.stream.ended_at)
        self.assertEqual(self.stream.viewer_count, 0)

    def test_end_stream_denies_non_owner(self):
        make_user("other")
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("end_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 403)
        self.stream.refresh_from_db()
        self.assertTrue(self.stream.is_live)

    def test_end_stream_denies_channel_mismatch(self):
        """A user with a channel that doesn't own the stream gets 403."""
        make_user("otherchan")
        self.client.login(username="otherchan", password="pass")
        response = self.client.post(reverse("end_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 403)

    def test_end_stream_not_found(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.post(reverse("end_stream", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_end_stream_requires_post(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("end_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 405)  # Method not allowed for View


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class WatchStreamViewTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream = Stream.objects.create(
            channel=self.channel,
            title="Watchable Stream",
            is_live=True,
        )

    def test_watch_stream_public(self):
        """Watch stream does not require authentication."""
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 200)

    def test_watch_stream_template(self):
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertTemplateUsed(response, "livestream/watch_stream.html")

    def test_watch_stream_shows_title(self):
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertContains(response, "Watchable Stream")

    def test_watch_stream_increments_viewer_count(self):
        self.assertEqual(self.stream.viewer_count, 0)
        self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.stream.refresh_from_db()
        self.assertEqual(self.stream.viewer_count, 1)

    def test_watch_stream_context_is_live(self):
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        stream = response.context["stream"]
        self.assertTrue(stream.is_live)

    def test_watch_stream_context_is_owner_authenticated(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertTrue(response.context["is_owner"])

    def test_watch_stream_context_is_owner_unauthenticated(self):
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertFalse(response.context["is_owner"])

    def test_watch_stream_context_subscriber_count(self):
        sub = make_user("sub")
        Subscription.objects.create(user=sub, channel=self.user)
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertEqual(response.context["subscriber_count"], 1)

    def test_watch_stream_context_subscribed(self):
        viewer = make_user("viewer")
        Subscription.objects.create(user=viewer, channel=self.user)
        self.client.login(username="viewer", password="pass")
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertTrue(response.context["is_subscribed"])

    def test_watch_stream_not_found(self):
        response = self.client.get(reverse("watch_stream", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_watch_stream_ended_stream(self):
        self.stream.is_live = False
        self.stream.ended_at = timezone.now()
        self.stream.save()
        response = self.client.get(reverse("watch_stream", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ended")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class StreamSettingsViewTests(TestCase):
    def setUp(self):
        self.user = make_user("streamer")
        self.channel = self.user.channel
        self.stream_key = StreamKey.objects.get(channel=self.channel)

    def test_settings_requires_login(self):
        response = self.client.get(reverse("stream_settings"))
        self.assertEqual(response.status_code, 302)

    def test_settings_get(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "livestream/stream_settings.html")

    def test_settings_shows_stream_key(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.get(reverse("stream_settings"))
        self.assertContains(response, self.stream_key.key)

    def test_settings_update_display_name(self):
        self.client.login(username="streamer", password="pass")
        response = self.client.post(
            reverse("stream_settings"),
            {"display_name": "My Gaming Key", "regenerate_key": False},
        )
        self.assertEqual(response.status_code, 302)
        self.stream_key.refresh_from_db()
        self.assertEqual(self.stream_key.display_name, "My Gaming Key")

    def test_settings_regenerate_key(self):
        self.client.login(username="streamer", password="pass")
        old_key = self.stream_key.key
        response = self.client.post(
            reverse("stream_settings"),
            {"display_name": "", "regenerate_key": True},
        )
        self.assertEqual(response.status_code, 302)
        self.stream_key.refresh_from_db()
        self.assertNotEqual(self.stream_key.key, old_key)

    def test_settings_no_channel(self):
        """User without a channel can still access settings but has_channel is False."""
        no_channel = make_user("nochan")
        no_channel.channel.delete()
        self.client.login(username="nochan", password="pass")
        response = self.client.get(reverse("stream_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_channel"])


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ChatMessageAPITests(TestCase):
    def setUp(self):
        self.user = make_user("chatter")
        streamer = make_user("streamer")
        self.channel = streamer.channel
        self.stream = Stream.objects.create(
            channel=self.channel, title="Chat Stream", is_live=True
        )
        self.client.login(username="chatter", password="pass")

    def test_chat_get_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("stream_chat", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 302)

    def test_chat_get_messages(self):
        ChatMessage.objects.create(stream=self.stream, user=self.user, message="Hello!")
        response = self.client.get(reverse("stream_chat", args=[self.stream.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["message"], "Hello!")
        self.assertEqual(data["messages"][0]["user"], "chatter")
        self.assertTrue(data["stream_live"])

    def test_chat_get_messages_after_id(self):
        m1 = ChatMessage.objects.create(
            stream=self.stream, user=self.user, message="First"
        )
        ChatMessage.objects.create(stream=self.stream, user=self.user, message="Second")
        response = self.client.get(
            f"{reverse('stream_chat', args=[self.stream.pk])}?after={m1.id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["message"], "Second")

    def test_chat_post_message(self):
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": "Hello stream!"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["message"], "Hello stream!")
        self.assertEqual(data["user"], "chatter")
        self.assertTrue(ChatMessage.objects.filter(message="Hello stream!").exists())

    def test_chat_post_empty_message(self):
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": ""},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("empty", data["error"].lower())

    def test_chat_post_message_too_long(self):
        long_msg = "x" * 501
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": long_msg},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("too long", data["error"].lower())

    def test_chat_post_stream_not_live(self):
        self.stream.is_live = False
        self.stream.save()
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": "Hello!"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("not live", data["error"].lower())

    def test_chat_post_rate_limit(self):
        """10 messages in 30s should be rate-limited."""
        for i in range(10):
            ChatMessage.objects.create(
                stream=self.stream,
                user=self.user,
                message=f"Message {i}",
            )
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": "One more"},
        )
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn("too fast", data["error"].lower())

    def test_chat_requires_login_to_post(self):
        self.client.logout()
        response = self.client.post(
            reverse("stream_chat", args=[self.stream.pk]),
            {"message": "Hello!"},
        )
        self.assertEqual(response.status_code, 302)

    def test_chat_stream_not_found(self):
        """Getting chat for a non-existent stream returns 404."""
        response = self.client.get(reverse("stream_chat", args=[9999]))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
#  Signal Tests
# ---------------------------------------------------------------------------


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class SignalTests(TestCase):
    def test_stream_key_created_on_channel_creation(self):
        user = make_user("newchan")
        self.assertTrue(StreamKey.objects.filter(channel=user.channel).exists())
        self.assertTrue(StreamKey.objects.get(channel=user.channel).is_active)

    def test_notification_on_go_live(self):
        """Verify the notify_subscribers_of_live_stream utility function."""
        streamer = make_user("streamer")
        subscriber = make_user("subscriber")
        Subscription.objects.create(user=subscriber, channel=streamer)
        channel = streamer.channel
        stream = Stream.objects.create(channel=channel, title="Test Live")

        from livestream.signals import notify_subscribers_of_live_stream

        notify_subscribers_of_live_stream(stream, streamer)
        self.assertTrue(
            Notification.objects.filter(
                recipient=subscriber,
                actor=streamer,
                verb="went_live",
            ).exists()
        )

    def test_notification_not_sent_to_self(self):
        """The actor should not receive their own live notification."""
        streamer = make_user("streamer")
        Subscription.objects.bulk_create(
            [Subscription(user=streamer, channel=streamer)]
        )
        channel = streamer.channel
        stream = Stream.objects.create(channel=channel, title="Self Live")

        from livestream.signals import notify_subscribers_of_live_stream

        notify_subscribers_of_live_stream(stream, streamer)
        self.assertFalse(
            Notification.objects.filter(
                recipient=streamer,
                actor=streamer,
                verb="went_live",
            ).exists()
        )
