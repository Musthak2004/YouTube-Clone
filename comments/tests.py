from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Comment
from videos.models import Video

User = get_user_model()


class CommentCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commenter', email='com@test.com', password='pass')
        self.uploader = User.objects.create_user(username='uploader', email='up@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )

    def test_create_comment_requires_login(self):
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Nice video!'}
        )
        self.assertEqual(response.status_code, 302)

    def test_create_comment(self):
        self.client.login(username='commenter', password='pass')
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Great content!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                user=self.user, video=self.video, text='Great content!'
            ).exists()
        )

    def test_create_comment_redirects_to_video(self):
        self.client.login(username='commenter', password='pass')
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Awesome!'}
        )
        self.assertRedirects(
            response, reverse('video_detail', args=[self.video.pk])
        )


class CommentEditTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@test.com', password='pass')
        self.other = User.objects.create_user(username='other', email='other@test.com', password='pass')
        self.uploader = User.objects.create_user(username='uploader_edit', email='up3@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )
        self.comment = Comment.objects.create(
            user=self.owner, video=self.video, text='Original comment'
        )

    def test_edit_page_status_code(self):
        self.client.login(username='owner', password='pass')
        response = self.client.get(reverse('comment_edit', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_comment(self):
        self.client.login(username='owner', password='pass')
        response = self.client.post(
            reverse('comment_edit', args=[self.comment.pk]),
            {'text': 'Updated comment'}
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment')

    def test_edit_denies_non_owner(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('comment_edit', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 403)

    def test_edit_requires_login(self):
        response = self.client.get(reverse('comment_edit', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 302)


class CommentDeleteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner2', email='owner2@test.com', password='pass')
        self.other = User.objects.create_user(username='other2', email='other2@test.com', password='pass')
        self.uploader = User.objects.create_user(username='uploader_del', email='up4@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )
        self.comment = Comment.objects.create(
            user=self.owner, video=self.video, text='Delete me'
        )

    def test_delete_page_status_code(self):
        self.client.login(username='owner2', password='pass')
        response = self.client.get(reverse('comment_delete', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_comment(self):
        self.client.login(username='owner2', password='pass')
        response = self.client.post(
            reverse('comment_delete', args=[self.comment.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_denies_non_owner(self):
        self.client.login(username='other2', password='pass')
        response = self.client.post(
            reverse('comment_delete', args=[self.comment.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_requires_login(self):
        response = self.client.get(reverse('comment_delete', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 302)


class CommentListTests(TestCase):
    def setUp(self):
        self.uploader = User.objects.create_user(username='uploader_list', email='up5@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )
        self.commenter = User.objects.create_user(username='commenter_list', email='comlist@test.com', password='pass')
        Comment.objects.create(
            user=self.commenter, video=self.video, text='First comment'
        )

    def test_comments_appear_on_video_detail(self):
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertContains(response, 'First comment')


class CommentModelTests(TestCase):
    def setUp(self):
        self.uploader = User.objects.create_user(username='up_model', email='upmodel@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Model Test'
        )
        self.commenter = User.objects.create_user(username='com_model', email='commodel@test.com', password='pass')

    def test_comment_string_representation(self):
        comment = Comment.objects.create(
            user=self.commenter, video=self.video, text='Nice!'
        )
        self.assertIn(str(self.commenter), str(comment))
        self.assertIn(str(self.video), str(comment))

    def test_created_at_is_auto_set(self):
        comment = Comment.objects.create(
            user=self.commenter, video=self.video, text='Timestamp test'
        )
        self.assertIsNotNone(comment.created_at)

    def test_updated_at_is_auto_set(self):
        comment = Comment.objects.create(
            user=self.commenter, video=self.video, text='Update test'
        )
        self.assertIsNotNone(comment.updated_at)

    def test_comment_redirects_to_video(self):
        comment = Comment.objects.create(
            user=self.commenter, video=self.video, text='Redirect test'
        )
        self.assertEqual(
            comment.get_absolute_url(),
            reverse('video_detail', args=[self.video.pk])
        )

    def test_parent_field_default_null(self):
        comment = Comment.objects.create(
            user=self.commenter, video=self.video, text='Top-level'
        )
        self.assertIsNone(comment.parent)

    def test_reply_has_parent(self):
        parent = Comment.objects.create(
            user=self.commenter, video=self.video, text='Parent'
        )
        reply = Comment.objects.create(
            user=self.commenter, video=self.video, parent=parent, text='Reply'
        )
        self.assertEqual(reply.parent, parent)
        self.assertIn(reply, parent.replies.all())


class CommentReplyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='replier', email='rep@test.com', password='pass')
        self.uploader = User.objects.create_user(username='uploader_rep', email='uprep@test.com', password='pass')
        self.video = Video.objects.create(
            uploader=self.uploader, title='Test Video'
        )
        self.parent_comment = Comment.objects.create(
            user=self.uploader, video=self.video, text='Original comment'
        )

    def test_create_reply_requires_login(self):
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'A reply', 'parent': self.parent_comment.pk}
        )
        self.assertEqual(response.status_code, 302)

    def test_create_reply(self):
        self.client.login(username='replier', password='pass')
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Nice reply!', 'parent': self.parent_comment.pk}
        )
        self.assertEqual(response.status_code, 302)
        reply = Comment.objects.filter(
            user=self.user, video=self.video, text='Nice reply!'
        ).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.parent, self.parent_comment)

    def test_reply_appears_in_parent_replies(self):
        self.client.login(username='replier', password='pass')
        self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Nested reply', 'parent': self.parent_comment.pk}
        )
        self.parent_comment.refresh_from_db()
        self.assertEqual(self.parent_comment.replies.count(), 1)

    def test_reply_shows_on_video_detail_page(self):
        self.client.login(username='replier', password='pass')
        self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Visible reply', 'parent': self.parent_comment.pk}
        )
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        self.assertContains(response, 'Visible reply')

    def test_reply_to_nonexistent_parent_returns_404(self):
        self.client.login(username='replier', password='pass')
        response = self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Orphan reply', 'parent': 99999}
        )
        self.assertEqual(response.status_code, 404)

    def test_top_level_comment_has_no_parent(self):
        self.client.login(username='replier', password='pass')
        self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Top level'}
        )
        comment = Comment.objects.get(text='Top level')
        self.assertIsNone(comment.parent)

    def test_reply_count_not_included_in_top_level_count(self):
        """Replies should not be counted as top-level comments on the video detail page."""
        self.client.login(username='replier', password='pass')
        # Create a top-level comment
        self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'Top level'}
        )
        # Create a reply
        self.client.post(
            reverse('comment_create', args=[self.video.pk]),
            {'text': 'A reply', 'parent': self.parent_comment.pk}
        )
        response = self.client.get(reverse('video_detail', args=[self.video.pk]))
        # There should be 2 top-level comments (the original + the one we just added)
        # The reply is nested and shouldn't add to the top-level count
        self.assertEqual(response.context['comment_count'], 2)
