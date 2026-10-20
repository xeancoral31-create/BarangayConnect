from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_UPLOAD_SIZE = 5 * 1024 * 1024
PDF_SIGNATURE = b'%PDF-'
IMAGE_FORMATS = {'JPEG', 'PNG', 'GIF', 'WEBP'}


def validate_document_upload(upload):
    """Validate size and actual file signature for resident-submitted documents."""
    if not upload:
        return upload
    if upload.size > MAX_UPLOAD_SIZE:
        raise ValidationError('File must be 5 MB or smaller.')
    try:
        upload.seek(0)
        header = upload.read(8)
        upload.seek(0)
        if header.startswith(PDF_SIGNATURE):
            return upload
        image = Image.open(upload)
        image.verify()
        if image.format not in IMAGE_FORMATS:
            raise ValidationError('Upload a valid PDF, JPEG, PNG, GIF, or WEBP file.')
        upload.seek(0)
        return upload
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError('Upload a valid PDF or image file.')
    finally:
        try:
            upload.seek(0)
        except (AttributeError, OSError):
            pass


def validate_image_upload(upload):
    """Validate raster images by decoding them instead of trusting the extension."""
    if not upload:
        return upload
    if upload.size > MAX_UPLOAD_SIZE:
        raise ValidationError('Image must be 5 MB or smaller.')
    try:
        upload.seek(0)
        image = Image.open(upload)
        image.verify()
        if image.format not in IMAGE_FORMATS:
            raise ValidationError('Upload a valid JPEG, PNG, GIF, or WEBP image.')
        upload.seek(0)
        return upload
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError('Upload a valid image file.')
    finally:
        try:
            upload.seek(0)
        except (AttributeError, OSError):
            pass
