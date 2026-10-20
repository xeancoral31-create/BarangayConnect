from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.cache import patch_cache_control

from accounts.models import CustomUser
from certificates.models import CertificateRequest
from complaints.models import Complaint


@login_required
def private_document(request, kind, pk):
    """Serve sensitive uploaded documents only to their owner or an active admin."""
    is_admin = request.user.is_active and request.user.is_admin()
    field = None
    owner_id = None

    if kind == 'resident-id':
        resident = get_object_or_404(CustomUser, pk=pk, role='resident')
        field = resident.valid_id
        owner_id = resident.pk
    elif kind in ('certificate-support', 'certificate-approved'):
        item = get_object_or_404(CertificateRequest.objects.select_related('resident'), pk=pk)
        field = item.supporting_document if kind == 'certificate-support' else item.approved_document
        owner_id = item.resident_id
    elif kind == 'complaint-support':
        item = get_object_or_404(Complaint.objects.select_related('resident'), pk=pk)
        field = item.supporting_document
        owner_id = item.resident_id
    else:
        raise Http404('Document not found.')

    if not is_admin and request.user.pk != owner_id:
        raise Http404('Document not found.')
    if not field:
        raise Http404('Document not found.')

    try:
        response = FileResponse(
            field.open('rb'),
            as_attachment=True,
            filename=Path(field.name).name,
            content_type='application/octet-stream',
        )
    except (FileNotFoundError, OSError, ValueError):
        raise Http404('Document not found.')
    patch_cache_control(response, private=True, no_store=True, no_cache=True, must_revalidate=True)
    response['X-Content-Type-Options'] = 'nosniff'
    return response
