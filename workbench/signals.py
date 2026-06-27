from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from grievances.models import Complaint
from appointments.models import Appointment
from .models import NotificationLog

STATUS_MESSAGES = {
    'in_progress': "Your complaint #{id} is now being worked on by our team.",
    'resolved': "Good news! Your complaint #{id} has been resolved.",
    'rejected': "Your complaint #{id} could not be processed. Please contact your local office for details.",
    'confirmed': "Your appointment #{id} (Token {token}) has been confirmed for {time}.",
    'completed': "Your appointment #{id} (Token {token}) is now complete.",
    'cancelled': "Your appointment #{id} (Token {token}) has been cancelled.",
}


def _track_previous_status(model):
    @receiver(pre_save, sender=model)
    def store_previous_status(sender, instance, **kwargs):
        if instance.pk:
            try:
                previous = sender.objects.get(pk=instance.pk)
                instance._previous_status = previous.status
            except sender.DoesNotExist:
                instance._previous_status = None
        else:
            instance._previous_status = None
    return store_previous_status


_track_previous_status(Complaint)
_track_previous_status(Appointment)


@receiver(post_save, sender=Complaint)
def notify_complaint_status_change(sender, instance, created, **kwargs):
    if created:
        return
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == instance.status:
        return

    template = STATUS_MESSAGES.get(instance.status)
    if not template:
        return

    message = template.format(id=instance.id)
    NotificationLog.objects.create(
        ticket_type='grievance',
        ticket_id=instance.id,
        recipient_user=instance.user,
        message=message,
        status_at_dispatch=instance.status,
    )


@receiver(post_save, sender=Appointment)
def notify_appointment_status_change(sender, instance, created, **kwargs):
    if created:
        return
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == instance.status:
        return

    template = STATUS_MESSAGES.get(instance.status)
    if not template:
        return

    message = template.format(
        id=instance.id,
        token=instance.token_number,
        time=instance.scheduled_time.strftime('%b %d, %Y at %I:%M %p'),
    )
    NotificationLog.objects.create(
        ticket_type='appointment',
        ticket_id=instance.id,
        recipient_user=instance.user,
        message=message,
        status_at_dispatch=instance.status,
    )