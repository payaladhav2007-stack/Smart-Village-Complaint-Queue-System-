from rest_framework import serializers
from django.utils import timezone
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = [
            'id',
            'service_type',
            'token_number',
            'scheduled_time',
            'status',
            'form_data_jsonb',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'token_number', 'status', 'created_at', 'updated_at']

    def validate_service_type(self, value):
        valid_types = [
            'birth_certificate',
            'death_certificate',
            'income_certificate',
            'residence_certificate',
            'caste_certificate',
            'property_certificate',
        ]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid service type. Must be one of: {', '.join(valid_types)}"
            )
        return value

    def validate_scheduled_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value

    def validate_form_data_jsonb(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "form_data_jsonb must be a valid JSON object."
            )
        if len(value) == 0:
            raise serializers.ValidationError(
                "form_data_jsonb must contain at least one field."
            )
        return value

