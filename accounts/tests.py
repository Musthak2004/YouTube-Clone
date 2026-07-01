from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpTests(TestCase):
    def test_signup_page_status_code(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post(reverse('signup'), data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_with_mismatched_passwords(self):
        response = self.client.post(reverse('signup'), data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_signup_with_existing_username(self):
        User.objects.create_user(username='testuser', email='existing@example.com', password='pass1234')
        response = self.client.post(reverse('signup'), data={
            'username': 'testuser',
            'email': 'other@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='login@example.com', password='testpass123'
        )

    def test_login_page_status_code(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class CustomUserModelTests(TestCase):
    def test_string_representation(self):
        user = User.objects.create_user(
            username='struser', email='str@test.com', password='pass123'
        )
        self.assertEqual(str(user), 'struser')

    def test_email_unique(self):
        User.objects.create_user(
            username='user1', email='same@test.com', password='pass123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2', email='same@test.com', password='pass123'
            )


class ChannelAutoCreationTests(TestCase):
    def test_channel_created_on_user_creation(self):
        from channels.models import Channel
        user = User.objects.create_user(
            username='newuser', email='new@test.com', password='pass123'
        )
        self.assertTrue(Channel.objects.filter(owner=user).exists())
        channel = Channel.objects.get(owner=user)
        self.assertEqual(channel.name, f"{user.username}'s Channel")

    def test_channel_has_correct_owner(self):
        from channels.models import Channel
        user = User.objects.create_user(
            username='owneruser', email='owner@test.com', password='pass123'
        )
        channel = Channel.objects.get(owner=user)
        self.assertEqual(channel.owner, user)


class PasswordChangeTests(TestCase):
    def test_password_change_requires_login(self):
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_page_status_code(self):
        User.objects.create_user(
            username='passuser', email='pass@test.com', password='oldpass123'
        )
        self.client.login(username='passuser', password='oldpass123')
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
