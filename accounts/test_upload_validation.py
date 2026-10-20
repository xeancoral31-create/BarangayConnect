from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from accounts.upload_validation import validate_document_upload, validate_image_upload


class UploadValidationTests(SimpleTestCase):
    def test_rejects_fake_pdf_with_invalid_signature(self):
        upload = SimpleUploadedFile('identity.pdf', b'not a real PDF document')
        with self.assertRaises(ValidationError):
            validate_document_upload(upload)

    def test_rejects_file_larger_than_limit(self):
        upload = SimpleUploadedFile('identity.pdf', b'%PDF-' + (b'x' * (5 * 1024 * 1024)))
        with self.assertRaises(ValidationError):
            validate_document_upload(upload)

    def test_rejects_invalid_image_bytes(self):
        upload = SimpleUploadedFile('profile.png', b'not an image')
        with self.assertRaises(ValidationError):
            validate_image_upload(upload)
