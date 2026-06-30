"""
GS-509: Post-test validation script
Run AFTER the Locust stress test finishes to confirm no duplicate
token numbers were created during concurrent booking attempts.

Run with:
    python manage.py shell < testing/load_tests/verify_no_duplicates.py
"""

from appointments.models import Appointment
from django.db.models import Count

print("Checking for duplicate token numbers...")

duplicates = (
    Appointment.objects
    .values('token_number')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

if duplicates.exists():
    print("FAILED: Duplicate tokens found!")
    for d in duplicates:
        print("  Token:", d['token_number'], "appears", d['count'], "times")
else:
    print("PASSED: No duplicate token numbers found.")
    total = Appointment.objects.count()
    print("Total appointments in database:", total)

print("Verification complete.")