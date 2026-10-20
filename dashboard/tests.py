from django.test import TestCase
from django.urls import reverse


class DashboardAuthenticationTests(TestCase):
    def test_resident_dashboard_requires_authentication(self):
        response = self.client.get(reverse('dashboard:resident_dashboard'))
        self.assertIn(response.status_code, (302, 403))

    def test_admin_dashboard_requires_authentication(self):
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertIn(response.status_code, (302, 403))
