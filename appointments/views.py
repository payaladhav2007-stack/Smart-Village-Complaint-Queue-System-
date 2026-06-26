from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from .utils import book_appointment_in_slot


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
                "appointment": AppointmentSerializer(appointment).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListMyAppointmentsView(ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.select_related('user').filter(
            user=self.request.user
        ).order_by('-scheduled_time')


def certificate_request(request):
    return render(request, 'appointments/certificate_request.html')


def queue_dashboard(request):
    return render(request, 'appointments/queue_dashboard.html')


def time_slot_picker(request):
    return render(request, 'appointments/time_slot_picker.html')


def token_confirmation(request):
    return render(request, 'appointments/token_confirmation.html')
