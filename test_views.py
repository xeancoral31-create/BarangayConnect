import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangayconnect.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser


if __name__ == '__main__':
    client = Client()
    
    print("--- Testing Guest Routes ---")
    res = client.get('/accounts/login/')
    assert res.status_code == 200, f"Login failed: {res.status_code}"
    assert res.content.decode().startswith('<!DOCTYPE html>'), "Login must start with <!DOCTYPE html>"
    print("GET /accounts/login/ -> 200 OK (Starts with <!DOCTYPE html>)")
    
    res = client.get('/accounts/register/')
    assert res.status_code == 200, f"Register failed: {res.status_code}"
    assert res.content.decode().startswith('<!DOCTYPE html>'), "Register must start with <!DOCTYPE html>"
    print("GET /accounts/register/ -> 200 OK (Starts with <!DOCTYPE html>)")
    
    print("\n--- Testing Resident Routes (juan_delacruz) ---")
    logged_in = client.login(username='juan_delacruz', password='resident12345')
    assert logged_in, "Resident login failed"
    
    routes = [
        '/dashboard/resident/',
        '/certificates/',
        '/certificates/request/',
        '/complaints/',
        '/complaints/submit/',
        '/announcements/',
        '/notifications/',
        '/accounts/profile/',
    ]
    
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Failed {r}: {res.status_code}"
        assert res.content.decode().startswith('<!DOCTYPE html>'), f"{r} must start with <!DOCTYPE html>"
        print(f"GET {r:30} -> 200 OK")
    
    client.logout()
    
    print("\n--- Testing Administrator Routes (admin) ---")
    logged_in = client.login(username='admin', password='admin12345')
    assert logged_in, "Admin login failed"
    
    admin_routes = [
        '/dashboard/admin/',
        '/accounts/admin/residents/',
        '/accounts/admin/officials/',
        '/certificates/admin/',
        '/certificates/admin/types/',
        '/complaints/admin/',
        '/announcements/admin/',
        '/reports/',
        '/audit/',
    ]
    
    for r in admin_routes:
        res = client.get(r)
        assert res.status_code == 200, f"Failed {r}: {res.status_code}"
        assert res.content.decode().startswith('<!DOCTYPE html>'), f"{r} must start with <!DOCTYPE html>"
        print(f"GET {r:30} -> 200 OK")
    
    print("\n--- ALL VIEW TESTS PASSED SUCCESSFULLY! ---")
    
