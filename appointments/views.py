from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import AppointmentSerializer
from .utils import book_appointment_in_slot
from .models import Appointment


class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment, error = book_appointment_in_slot(
                user=request.user,
                service_type=serializer.validated_data['service_type'],
                scheduled_time=serializer.validated_data['scheduled_time'],
                form_data_jsonb=serializer.validated_data['form_data_jsonb'],
            )
            if error:
                return Response({"error": error}, status=status.HTTP_409_CONFLICT)
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


class ListMyAppointmentsView(ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-scheduled_time')