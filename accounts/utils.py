from django.urls import reverse

def get_dashboard_url(user):
    return {
        'citizen':  reverse('my_complaints'),
        'staff':    reverse('staff_dashboard'),
        'sarpanch': reverse('sarpanch_dashboard'),
    }.get(getattr(user, 'role', ''), reverse('home'))
