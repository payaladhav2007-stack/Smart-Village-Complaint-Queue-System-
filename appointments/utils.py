from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Appointment

SLOT_DURATION_MINUTES = 30
SLOT_CAPACITY = 10  # max appointments per slot


def get_slot_window(scheduled_time):
    """Round scheduled_time down to its slot block start."""
    minute_block = (scheduled_time.minute // SLOT_DURATION_MINUTES) * SLOT_DURATION_MINUTES
    return scheduled_time.replace(minute=minute_block, second=0, microsecond=0)


def book_appointment_in_slot(user, service_type, scheduled_time, form_data_jsonb):
    """
    Atomically checks slot capacity and books the appointment.
    Uses select_for_update to lock matching rows and prevent race conditions
    when multiple requests hit the same slot at the same time.
    """
    slot_start = get_slot_window(scheduled_time)
    slot_end = slot_start + timedelta(minutes=SLOT_DURATION_MINUTES)

    with transaction.atomic():
        existing_count = Appointment.objects.select_for_update().filter(
            scheduled_time__gte=slot_start,
            scheduled_time__lt=slot_end,
        ).count()

        if existing_count >= SLOT_CAPACITY:
            return None, "This time slot is full. Please choose a different time."

        token_number = generate_sequential_token()

        appointment = Appointment.objects.create(
            user=user,
            service_type=service_type,
            scheduled_time=scheduled_time,
            token_number=token_number,
            form_data_jsonb=form_data_jsonb,
            status='pending',
        )
        return appointment, None


def generate_sequential_token():
    """
    Generates the next sequential token, e.g. Token #012.
    Locks the last row to avoid two requests computing the same next number.
    """
    last = Appointment.objects.select_for_update().order_by('-id').first()
    next_number = (last.id + 1) if last else 1
    return f"#{next_number:03d}"