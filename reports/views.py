import csv
import io
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from accounts.models import CustomUser
from certificates.models import CertificateRequest, CertificateType
from complaints.models import Complaint
from announcements.models import Announcement
from accounts.views import admin_required


def _safe_csv_cell(value):
    """Prevent spreadsheet formula execution in exported user-controlled cells."""
    if value is None:
        return ''
    text = str(value)
    if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + text
    return text

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@admin_required
def reports_dashboard(request):
    context = {
        'total_residents': CustomUser.objects.filter(role='resident').count(),
        'active_residents': CustomUser.objects.filter(role='resident', account_status='active').count(),
        'inactive_residents': CustomUser.objects.filter(role='resident', account_status='inactive').count(),
        'pending_residents': CustomUser.objects.filter(role='resident', account_status='pending').count(),
        'total_requests': CertificateRequest.objects.count(),
        'requests_by_status': CertificateRequest.objects.values('status').annotate(count=Count('id')),
        'requests_by_type': CertificateRequest.objects.values('certificate_type__name').annotate(count=Count('id')).order_by('-count'),
        'total_complaints': Complaint.objects.count(),
        'complaints_by_status': Complaint.objects.values('status').annotate(count=Count('id')),
        'complaints_by_category': Complaint.objects.values('category').annotate(count=Count('id')).order_by('-count'),
        'total_announcements': Announcement.objects.filter(status='published').count(),
    }
    return render(request, 'reports/dashboard.html', context)


@admin_required
def export_residents_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="residents_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Username', 'Email', 'Phone', 'Gender', 'Civil Status', 'Barangay', 'Status', 'Date Registered'])
    residents = CustomUser.objects.filter(role='resident').order_by('-created_at')
    for r in residents:
        writer.writerow([
            *[_safe_csv_cell(value) for value in (r.get_full_name(), r.username, r.email, r.phone,
            r.get_gender_display(), r.get_civil_status_display(), r.barangay,
            r.get_account_status_display(),
            r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
            )],
        ])
    return response


@admin_required
def export_requests_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="certificate_requests_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Resident Name', 'Certificate Type', 'Purpose', 'Copies', 'Status', 'Date Submitted', 'Date Updated'])
    requests = CertificateRequest.objects.select_related('resident', 'certificate_type').order_by('-created_at')
    for req in requests:
        writer.writerow([_safe_csv_cell(value) for value in [
            req.resident.get_full_name(), req.certificate_type.name,
            req.purpose, req.copies, req.get_status_display(),
            req.created_at.strftime('%Y-%m-%d %H:%M'),
            req.updated_at.strftime('%Y-%m-%d %H:%M'),
        ]])
    return response


@admin_required
def export_complaints_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Resident', 'Subject', 'Category', 'Status', 'Date Submitted', 'Date Updated'])
    complaints = Complaint.objects.select_related('resident').order_by('-created_at')
    for c in complaints:
        writer.writerow([_safe_csv_cell(value) for value in [
            c.resident.get_full_name(), c.subject,
            c.get_category_display(), c.get_status_display(),
            c.created_at.strftime('%Y-%m-%d %H:%M'),
            c.updated_at.strftime('%Y-%m-%d %H:%M'),
        ]])
    return response


@admin_required
def export_residents_pdf(request):
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("PDF export unavailable.", status=503)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, spaceAfter=12)

    elements.append(Paragraph("BarangayConnect — Residents Report", title_style))
    elements.append(Spacer(1, 12))

    data = [['Full Name', 'Username', 'Email', 'Status', 'Registered']]
    residents = CustomUser.objects.filter(role='resident').order_by('-created_at')
    for r in residents:
        data.append([
            r.get_full_name(), r.username, r.email,
            r.get_account_status_display(),
            r.created_at.strftime('%Y-%m-%d') if r.created_at else '',
        ])

    table = Table(data, colWidths=[1.6*inch, 1.2*inch, 2*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f4f8')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf',
                        headers={'Content-Disposition': 'attachment; filename="residents_report.pdf"'})
