from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from notifications.models import Notification


class NotificationMethodTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='notification_user',
            password='StrongTestPass!234',
            role='resident',
            account_status='active',
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test notification',
            message='Test message',
            notification_type='account',
        )
        self.client.login(username='notification_user', password='StrongTestPass!234')

    def test_get_list_does_not_mark_notifications_read(self):
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_mark_single_read_rejects_get(self):
        response = self.client.get(reverse('notifications:mark_read', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 405)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_mark_all_read_rejects_get(self):
        response = self.client.get(reverse('notifications:mark_all_read'))
        self.assertEqual(response.status_code, 405)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_mark_all_read_accepts_post(self):
        response = self.client.post(reverse('notifications:mark_all_read'))
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
