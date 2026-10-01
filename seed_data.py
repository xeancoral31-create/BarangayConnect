import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangayconnect.settings')
django.setup()

from django.utils import timezone
from accounts.models import CustomUser, BarangayOfficial, SystemSetting
from certificates.models import CertificateType, CertificateRequest
from complaints.models import Complaint
from announcements.models import Announcement
from notifications.models import Notification

print("Seeding BarangayConnect initial data...")

# 1. Admin User
admin_user, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'first_name': 'Barangay',
        'last_name': 'Administrator',
        'email': 'admin@barangayconnect.gov.ph',
        'role': 'admin',
        'account_status': 'active',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)
admin_user.set_password('admin12345')
admin_user.save()
print("Admin user ready: admin / admin12345")

# 2. Resident Users
resident1, _ = CustomUser.objects.get_or_create(
    username='juan_delacruz',
    defaults={
        'first_name': 'Juan',
        'last_name': 'Dela Cruz',
        'email': 'juan@example.com',
        'phone': '0917-123-4567',
        'role': 'resident',
        'account_status': 'active',
        'gender': 'M',
        'civil_status': 'married',
        'address': 'Block 12 Lot 4, Mabini Street, Barangay San Isidro',
        'barangay': 'San Isidro',
        'is_active': True,
    }
)
resident1.set_password('resident12345')
resident1.save()
print("Resident user ready: juan_delacruz / resident12345")

resident2, _ = CustomUser.objects.get_or_create(
    username='maria_santos',
    defaults={
        'first_name': 'Maria',
        'last_name': 'Santos',
        'email': 'maria@example.com',
        'phone': '0928-765-4321',
        'role': 'resident',
        'account_status': 'pending',
        'gender': 'F',
        'civil_status': 'single',
        'address': 'Phase 2, Rizal Avenue, Barangay San Isidro',
        'barangay': 'San Isidro',
        'is_active': True,
    }
)
resident2.set_password('resident12345')
resident2.save()
print("Resident user ready: maria_santos / resident12345")

# 3. Certificate Types
types_data = [
    {
        'name': 'Barangay Clearance',
        'description': 'General clearance certifying good moral character and no derogatory record.',
        'fee': 50.00,
        'processing_days': 1,
        'requirements': 'Valid ID and 6 months residency verification.',
    },
    {
        'name': 'Certificate of Residency',
        'description': 'Certifies that the named resident is a bona fide resident of the barangay.',
        'fee': 50.00,
        'processing_days': 1,
        'requirements': 'Government-issued ID or utility bill.',
    },
    {
        'name': 'Certificate of Indigency',
        'description': 'Issued for medical assistance, legal aid, scholarship, and social welfare programs.',
        'fee': 0.00,
        'processing_days': 1,
        'requirements': 'Case assessment by the Barangay Social Worker / Lupong Tagapamayapa.',
    },
    {
        'name': 'Barangay Business Clearance',
        'description': 'Required permit for small businesses and commercial establishments operating within the barangay.',
        'fee': 200.00,
        'processing_days': 2,
        'requirements': 'DTI registration, lease contract / tax declaration.',
    },
]

for td in types_data:
    ct, _ = CertificateType.objects.get_or_create(name=td['name'], defaults=td)
    print(f"Certificate Type: {ct.name}")

# 4. Barangay Officials
officials_data = [
    {
        'name': 'Eduardo Manalo',
        'position': 'punong_barangay',
        'committee': 'Executive & Peace and Order Committee',
        'contact': '0917-555-0101',
        'email': 'punongbarangay@sanisidro.gov.ph',
        'order': 1,
    },
    {
        'name': 'Lorna Reyes',
        'position': 'kagawad',
        'committee': 'Committee on Health and Sanitation',
        'contact': '0918-555-0102',
        'email': 'kagawad.reyes@sanisidro.gov.ph',
        'order': 2,
    },
    {
        'name': 'Carlos Bautista',
        'position': 'kagawad',
        'committee': 'Committee on Public Works and Infrastructure',
        'contact': '0920-555-0103',
        'email': 'kagawad.bautista@sanisidro.gov.ph',
        'order': 3,
    },
    {
        'name': 'Beatriz Aquino',
        'position': 'sk_chairman',
        'committee': 'Committee on Youth & Sports Development',
        'contact': '0922-555-0104',
        'email': 'sk.aquino@sanisidro.gov.ph',
        'order': 4,
    },
    {
        'name': 'Rodrigo Cruz',
        'position': 'secretary',
        'committee': 'Barangay Records & Administration',
        'contact': '0927-555-0105',
        'email': 'sec.cruz@sanisidro.gov.ph',
        'order': 5,
    },
]

for od in officials_data:
    bo, _ = BarangayOfficial.objects.get_or_create(
        name=od['name'],
        position=od['position'],
        defaults=od
    )
    print(f"Official: {bo.name} ({bo.get_position_display()})")

# 5. Announcements
announcements_data = [
    {
        'title': 'Free Community Health Screening and Medical Mission',
        'status': 'published',
        'content': (
            'The Barangay Health Station in cooperation with the City Health Department '
            'will conduct a free medical checkup, dental extraction, and distribution of maintenance '
            'medicines this coming Saturday from 8:00 AM to 3:00 PM at the Covered Court.\n\n'
            'Please bring your PhilHealth ID or Barangay ID.'
        ),
        'published_at': timezone.now(),
        'author': admin_user,
    },
    {
        'title': 'General Barangay Assembly for the Current Quarter',
        'status': 'published',
        'content': (
            'All registered residents and household heads are invited to attend our upcoming '
            'Barangay Assembly on the last Sunday of this month at 2:00 PM in the Barangay Multi-purpose Hall.\n\n'
            'Agenda includes financial reports, upcoming project presentations, and open community forum.'
        ),
        'published_at': timezone.now(),
        'author': admin_user,
    },
    {
        'title': 'Typhoon Preparedness and Emergency Hotline Advisory',
        'status': 'published',
        'content': (
            'In light of the weather disturbance advisory from PAGASA, the Barangay Disaster Risk Reduction '
            'and Management Council (BDRRMC) is on heightened alert.\n\n'
            'Barangay Emergency Hotline: (02) 8123-4567 / 0917-999-BDRR.\n'
            'Evacuation centers are prepared at the Elementary School Gym.'
        ),
        'published_at': timezone.now(),
        'author': admin_user,
    },
]

for ad in announcements_data:
    ann, _ = Announcement.objects.get_or_create(
        title=ad['title'],
        defaults=ad
    )
    print(f"Announcement: {ann.title}")

# 6. Sample Certificate Request
clearance_type = CertificateType.objects.filter(name='Barangay Clearance').first()
if clearance_type and resident1:
    cr, _ = CertificateRequest.objects.get_or_create(
        resident=resident1,
        certificate_type=clearance_type,
        defaults={
            'purpose': 'Local employment application requirement',
            'status': 'ready',
            'remarks': 'Approved and signed by Punong Barangay. Ready for claiming at Window 1.',
        }
    )
    print(f"Sample Request ID: {cr.id}")

# 7. Sample Complaint
if resident1:
    comp, _ = Complaint.objects.get_or_create(
        resident=resident1,
        subject='Excessive noise disturbance past curfew hours',
        defaults={
            'category': 'noise',
            'location': 'Mabini Street corner Bonifacio',
            'incident_date': timezone.now().date(),
            'description': (
                'Loud videoke and motorcycle revving persisting beyond 11:00 PM along Mabini Street, '
                'causing disturbance to students studying and elderly residents resting.'
            ),
            'status': 'in_progress',
            'admin_response': (
                'Barangay Tanods have been dispatched to issue verbal warning to the residents concerned. '
                'Patrol frequency increased in the area.'
            ),
        }
    )
    print(f"Sample Complaint ID: {comp.id}")

# 8. Sample Notifications
Notification.objects.get_or_create(
    recipient=resident1,
    title='Certificate Ready for Pickup',
    defaults={
        'message': 'Your Barangay Clearance is approved and ready for pickup at the barangay hall window 1.',
        'notification_type': 'certificate',
    }
)

Notification.objects.get_or_create(
    recipient=resident1,
    title='Complaint Case Update',
    defaults={
        'message': 'Your report regarding noise disturbance has been updated to In Progress by Barangay Peace and Order staff.',
        'notification_type': 'complaint',
    }
)

print("\n--- Seed Data Process Completed Successfully! ---")
