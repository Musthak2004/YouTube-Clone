from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from videos.models import Video

from .models import Playlist, PlaylistItem

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
class PlaylistCreateTests(TestCase):
    def setUp(self):
        self.user = make_user("creator")
        self.client.login(username="creator", password="pass")

    def test_create_page_status_code(self):
        response = self.client.get(reverse("playlist_create"))
        self.assertEqual(response.status_code, 200)

    def test_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("playlist_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_playlist(self):
        response = self.client.post(
            reverse("playlist_create"),
            {
                "title": "My Favorites",
                "description": "My best videos",
                "visibility": "public",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Playlist.objects.filter(title="My Favorites").exists())

    def test_create_sets_owner(self):
        self.client.post(
            reverse("playlist_create"),
            {
                "title": "My Playlist",
                "description": "",
                "visibility": "public",
            },
        )
        playlist = Playlist.objects.get(title="My Playlist")
        self.assertEqual(playlist.owner, self.user)

    def test_create_ajax_success(self):
        response = self.client.post(
            reverse("playlist_create"),
            {"title": "Quick List", "visibility": "public"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Quick List")

    def test_create_ajax_invalid(self):
        response = self.client.post(
            reverse("playlist_create"),
            {"title": "", "visibility": "invalid"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PlaylistListTests(TestCase):
    def setUp(self):
        self.user = make_user("owner")
        self.other = make_user("other")
        self.client.login(username="owner", password="pass")
        for i in range(3):
            Playlist.objects.create(
                owner=self.user, title=f"List {i}", visibility="public"
            )
        # Other user's playlist — should not appear
        Playlist.objects.create(owner=self.other, title="Not Mine", visibility="public")

    def test_list_status_code(self):
        response = self.client.get(reverse("playlist_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        response = self.client.get(reverse("playlist_list"))
        self.assertTemplateUsed(response, "playlists/playlist_list.html")

    def test_list_shows_own_playlists(self):
        response = self.client.get(reverse("playlist_list"))
        self.assertContains(response, "List 0")
        self.assertContains(response, "List 1")
        self.assertContains(response, "List 2")

    def test_list_hides_other_playlists(self):
        response = self.client.get(reverse("playlist_list"))
        self.assertNotContains(response, "Not Mine")

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("playlist_list"))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_total_videos_in_context(self):
        video = make_uploaded_video(self.user)
        pl = Playlist.objects.get(owner=self.user, title="List 0")
        PlaylistItem.objects.create(playlist=pl, video=video)
        response = self.client.get(reverse("playlist_list"))
        self.assertIn("total_videos", response.context)

    def test_list_shows_empty_state(self):
        Playlist.objects.filter(owner=self.user).delete()
        response = self.client.get(reverse("playlist_list"))
        self.assertContains(response, "No playlists yet")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PlaylistDetailTests(TestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.other = make_user("other")
        self.client.login(username="owner", password="pass")
        self.playlist = Playlist.objects.create(
            owner=self.owner, title="My List", visibility="public"
        )

    def test_detail_status_code(self):
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertTemplateUsed(response, "playlists/playlist_detail.html")

    def test_detail_shows_playlist_title(self):
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertContains(response, "My List")

    def test_detail_public_visible_to_anyone(self):
        self.client.logout()
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_private_redirects_non_owner(self):
        self.playlist.visibility = "private"
        self.playlist.save()
        # Login the non-owner user so the redirect chain can complete
        self.client.logout()
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertRedirects(response, reverse("playlist_list"))

    def test_detail_private_visible_to_owner(self):
        self.playlist.visibility = "private"
        self.playlist.save()
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_shows_videos(self):
        video = make_uploaded_video(self.owner)
        PlaylistItem.objects.create(playlist=self.playlist, video=video, order=0)
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertContains(response, video.title)

    def test_detail_is_owner_true(self):
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertTrue(response.context["is_owner"])

    def test_detail_is_owner_false(self):
        self.client.logout()
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("playlist_detail", args=[self.playlist.pk]))
        self.assertFalse(response.context["is_owner"])


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PlaylistUpdateDeleteTests(TestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.other = make_user("other")
        self.client.login(username="owner", password="pass")
        self.playlist = Playlist.objects.create(
            owner=self.owner, title="My List", visibility="public"
        )

    def test_update_page_status_code(self):
        response = self.client.get(reverse("playlist_update", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 200)

    def test_update_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("playlist_update", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 302)

    def test_update_owner_allowed(self):
        response = self.client.post(
            reverse("playlist_update", args=[self.playlist.pk]),
            {"title": "Updated", "description": "changed", "visibility": "private"},
        )
        self.assertEqual(response.status_code, 302)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.title, "Updated")
        self.assertEqual(self.playlist.visibility, "private")

    def test_update_non_owner_blocked(self):
        self.client.logout()
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("playlist_update", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 403)

    def test_delete_page_status_code(self):
        response = self.client.get(reverse("playlist_delete", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_owner_allowed(self):
        response = self.client.post(reverse("playlist_delete", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Playlist.objects.filter(pk=self.playlist.pk).exists())

    def test_delete_non_owner_blocked(self):
        self.client.logout()
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("playlist_delete", args=[self.playlist.pk]))
        self.assertEqual(response.status_code, 403)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class AddToPlaylistTests(TestCase):
    def setUp(self):
        self.user = make_user("saver")
        self.other = make_user("other")
        self.client.login(username="saver", password="pass")
        self.video = make_uploaded_video(self.user)
        self.playlist = Playlist.objects.create(
            owner=self.user, title="My List", visibility="public"
        )

    def test_add_video_to_playlist(self):
        response = self.client.post(
            reverse("playlist_add_video", args=[self.video.pk]),
            {"playlist_ids": [str(self.playlist.pk)]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            PlaylistItem.objects.filter(
                playlist=self.playlist, video=self.video
            ).exists()
        )

    def test_remove_video_from_playlist(self):
        PlaylistItem.objects.create(playlist=self.playlist, video=self.video)
        response = self.client.post(
            reverse("playlist_add_video", args=[self.video.pk]),
            {"playlist_ids": []},  # empty = remove from all
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PlaylistItem.objects.filter(
                playlist=self.playlist, video=self.video
            ).exists()
        )

    def test_add_video_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse("playlist_add_video", args=[self.video.pk]),
            {"playlist_ids": [str(self.playlist.pk)]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PlaylistItem.objects.filter(
                playlist=self.playlist, video=self.video
            ).exists()
        )

    def test_add_to_other_users_playlist_ignored(self):
        other_pl = Playlist.objects.create(
            owner=self.other, title="Not Mine", visibility="public"
        )
        response = self.client.post(
            reverse("playlist_add_video", args=[self.video.pk]),
            {"playlist_ids": [str(other_pl.pk)]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PlaylistItem.objects.filter(playlist=other_pl, video=self.video).exists()
        )


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PlaylistItemTests(TestCase):
    def setUp(self):
        self.user = make_user("owner")
        self.client.login(username="owner", password="pass")
        self.playlist = Playlist.objects.create(
            owner=self.user, title="Ordered", visibility="public"
        )
        self.video_a = make_uploaded_video(self.user, title="Video A")
        self.video_b = make_uploaded_video(self.user, title="Video B")

    def test_unique_constraint(self):
        PlaylistItem.objects.create(playlist=self.playlist, video=self.video_a)
        with self.assertRaises(Exception):
            PlaylistItem.objects.create(playlist=self.playlist, video=self.video_a)

    def test_ordering_default(self):
        item_a = PlaylistItem.objects.create(
            playlist=self.playlist, video=self.video_a, order=1
        )
        item_b = PlaylistItem.objects.create(
            playlist=self.playlist, video=self.video_b, order=0
        )
        items = list(self.playlist.items.all())
        self.assertEqual(items[0], item_b)
        self.assertEqual(items[1], item_a)

    def test_str_method(self):
        item = PlaylistItem.objects.create(playlist=self.playlist, video=self.video_a)
        expected = f"{self.video_a.title} in {self.playlist.title}"
        self.assertEqual(str(item), expected)

    def test_playlist_items_count(self):
        PlaylistItem.objects.create(playlist=self.playlist, video=self.video_a)
        PlaylistItem.objects.create(playlist=self.playlist, video=self.video_b)
        self.assertEqual(self.playlist.items.count(), 2)


def make_uploaded_video(user, title="Test Video"):
    video_file = SimpleUploadedFile(
        "test.mp4", b"file_content", content_type="video/mp4"
    )
    return Video.objects.create(
        uploader=user,
        title=title,
        description="A test video",
        video_file=video_file,
    )
