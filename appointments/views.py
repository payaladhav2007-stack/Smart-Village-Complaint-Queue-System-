from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import uuid
from .models import Appointment
from .serializers import AppointmentSerializer

class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            # Generate unique token number
            token_number = f"TKN-{uuid.uuid4().hex[:6].upper()}"

            # Save appointment with user and token
            appointment = serializer.save(
                user=request.user,
                token_number=token_number,
                status='pending'
            )

            return Response({
                "message": "Appointment booked successfully.",
                "appointment": {
                    "id": appointment.id,
                    "service_type": appointment.service_type,
                    "token_number": appointment.token_number,
                    "scheduled_time": str(appointment.scheduled_time),
                    "status": appointment.status,
                    "form_data_jsonb": appointment.form_data_jsonb,
                    "created_at": str(appointment.created_at)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
