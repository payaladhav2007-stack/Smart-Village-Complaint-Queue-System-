import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import SmsOtp

User = get_user_model()
OTP_VALIDITY_MINUTES = 5


@csrf_exempt
def request_otp(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        phone_number = payload.get('phone_number', '').strip()

        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'phone_number is required'}, status=400)

        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            code = SmsOtp.generate_code()
            SmsOtp.objects.create(
                phone_number=phone_number,
                code=code,
                expires_at=timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES),
            )
            print(f"[SMS_AUTH] OTP for {phone_number}: {code}")
        else:
            print(f"[SMS_AUTH] OTP requested for unknown number: {phone_number}")

        return JsonResponse({'status': 'otp_sent'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)


@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        phone_number = payload.get('phone_number', '').strip()
        otp_code = payload.get('otp_code', '').strip()

        if not phone_number or not otp_code:
            return JsonResponse({'status': 'error', 'message': 'phone_number and otp_code are required'}, status=400)

        otp = SmsOtp.objects.filter(
            phone_number=phone_number
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid(otp_code):
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired code'}, status=400)

        otp.is_used = True
        otp.save()

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired code'}, status=400)

        return JsonResponse({
            'status': 'success',
            'message': 'User identity resolved',
            'user_id': user.id,
            'username': user.username,
            'ward_number': user.ward_number,
            'phone_number': user.phone_number,
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
     


