from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class PrivateDocumentAccessTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username='document_owner',
            password='StrongTestPass!234',
            role='resident',
            account_status='active',
        )
        self.other = CustomUser.objects.create_user(
            username='other_resident',
            password='StrongTestPass!234',
            role='resident',
            account_status='active',
        )

    def test_other_resident_cannot_access_resident_id(self):
        self.client.login(username='other_resident', password='StrongTestPass!234')
        response = self.client.get(
            reverse('accounts:private_document', args=['resident-id', self.owner.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_document_kind_is_not_found(self):
        self.client.login(username='document_owner', password='StrongTestPass!234')
        response = self.client.get(
            reverse('accounts:private_document', args=['unknown-kind', self.owner.pk])
        )
        self.assertEqual(response.status_code, 404)
