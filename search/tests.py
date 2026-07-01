from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from videos.models import Video
from .models import SearchHistory

User = get_user_model()


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class SearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='searcher', email='search@test.com', password='pass'
        )
        self.uploader = User.objects.create_user(
            username='uploader_searched', email='upsearch@test.com', password='pass'
        )
        self.video = Video.objects.create(
            uploader=self.uploader,
            title='Python Django Tutorial',
            description='Learn Django step by step',
        )

    def test_search_page_no_query(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type something above to search')

    def test_search_page_with_query(self):
        response = self.client.get(reverse('search'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Django Tutorial')

    def test_search_no_results(self):
        response = self.client.get(reverse('search'), {'q': 'xyznonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No results found')

    def test_search_empty_query(self):
        response = self.client.get(reverse('search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type something above to search')

    def test_search_blank_query(self):
        response = self.client.get(reverse('search'), {'q': '   '})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type something above to search')

    def test_search_total_count_in_context(self):
        response = self.client.get(reverse('search'), {'q': 'Django'})
        self.assertEqual(response.context['total_count'], 1)

    def test_search_description_match(self):
        response = self.client.get(reverse('search'), {'q': 'step by step'})
        self.assertContains(response, 'Python Django Tutorial')


class SearchHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hist_user', email='hist@test.com', password='pass'
        )

    def test_search_creates_history_when_authenticated(self):
        self.client.login(username='hist_user', password='pass')
        self.client.get(reverse('search'), {'q': 'test query'})
        self.assertTrue(
            SearchHistory.objects.filter(
                user=self.user, query='test query'
            ).exists()
        )

    def test_search_does_not_create_history_when_anonymous(self):
        self.client.get(reverse('search'), {'q': 'test query'})
        self.assertEqual(SearchHistory.objects.count(), 0)

    def test_search_history_recent_in_context(self):
        self.client.login(username='hist_user', password='pass')
        self.client.get(reverse('search'), {'q': 'recent query'})
        response = self.client.get(reverse('search'))
        self.assertEqual(len(response.context['recent_history']), 1)

    def test_search_history_shows_in_sidebar(self):
        self.client.login(username='hist_user', password='pass')
        self.client.get(reverse('search'), {'q': 'sidebar query'})
        response = self.client.get(reverse('search'))
        self.assertContains(response, 'sidebar query')


class ClearSearchHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='clear_user', email='clear@test.com', password='pass'
        )
        SearchHistory.objects.create(user=self.user, query='q1')
        SearchHistory.objects.create(user=self.user, query='q2')

    def test_clear_history(self):
        self.client.login(username='clear_user', password='pass')
        self.client.post(reverse('search_history_clear'))
        self.assertEqual(
            SearchHistory.objects.filter(user=self.user).count(), 0
        )

    def test_clear_history_redirects(self):
        self.client.login(username='clear_user', password='pass')
        response = self.client.post(reverse('search_history_clear'))
        self.assertRedirects(response, reverse('search'))


class DeleteSearchHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='del_user', email='delhist@test.com', password='pass'
        )
        self.history = SearchHistory.objects.create(
            user=self.user, query='delete me'
        )

    def test_delete_history_entry(self):
        self.client.login(username='del_user', password='pass')
        self.client.post(
            reverse('search_history_delete', args=[self.history.pk])
        )
        self.assertFalse(
            SearchHistory.objects.filter(pk=self.history.pk).exists()
        )

    def test_delete_history_redirects(self):
        self.client.login(username='del_user', password='pass')
        response = self.client.post(
            reverse('search_history_delete', args=[self.history.pk])
        )
        self.assertRedirects(response, reverse('search'))

    def test_cannot_delete_others_history(self):
        other_user = User.objects.create_user(
            username='other_hist', email='otherhist@test.com', password='pass'
        )
        self.client.login(username='other_hist', password='pass')
        self.client.post(
            reverse('search_history_delete', args=[self.history.pk])
        )
        # The view uses filter(pk=pk, user=user) so other users cannot delete
        self.assertTrue(
            SearchHistory.objects.filter(pk=self.history.pk).exists()
        )
