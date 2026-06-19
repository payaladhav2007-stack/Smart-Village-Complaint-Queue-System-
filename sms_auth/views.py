from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@csrf_exempt
def sms_auth_endpoint(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        phone_number = payload.get('phone_number', '').strip()

        if not phone_number:
            return JsonResponse({
                'status': 'error',
                'message': 'phone_number is required'
            }, status=400)

        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            return JsonResponse({
                'status': 'success',
                'message': 'User identity resolved',
                'user_id': user.id,
                'username': user.username,
                'ward_number': user.ward_number,
                'phone_number': user.phone_number,
            }, status=200)
        else:
            return JsonResponse({
                'status': 'failure',
                'message': 'No active user found for this phone number'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON payload'
        }, status=400)


