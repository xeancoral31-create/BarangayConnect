from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class ResidentAccessControlTests(TestCase):
    def make_resident(self, status='active', is_active=True):
        return CustomUser.objects.create_user(
            username=f'resident_{status}',
            password='StrongTestPass!234',
            role='resident',
            account_status=status,
            is_active=is_active,
        )

    def test_pending_resident_cannot_access_resident_dashboard(self):
        self.make_resident(status='pending')
        self.client.login(username='resident_pending', password='StrongTestPass!234')
        response = self.client.get(reverse('dashboard:resident_dashboard'))
        self.assertIn(response.status_code, (302, 403))

    def test_inactive_resident_cannot_access_resident_dashboard(self):
        self.make_resident(status='inactive', is_active=False)
        self.client.login(username='resident_inactive', password='StrongTestPass!234')
        response = self.client.get(reverse('dashboard:resident_dashboard'))
        self.assertIn(response.status_code, (302, 403))
