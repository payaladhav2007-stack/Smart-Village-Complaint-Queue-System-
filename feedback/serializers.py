from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from grievances.models import Complaint
from appointments.models import Appointment
from .models import Feedback


class FeedbackSubmitSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=['grievance', 'appointment'])
    target_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        model = Complaint if data['target_type'] == 'grievance' else Appointment
        completed_status = 'resolved' if data['target_type'] == 'grievance' else 'completed'

        try:
            target = model.objects.get(id=data['target_id'])
        except model.DoesNotExist:
            raise serializers.ValidationError(
                f"No {data['target_type']} found with id {data['target_id']}."
            )

        if target.status != completed_status:
            raise serializers.ValidationError(
                f"Feedback can only be submitted once the {data['target_type']} is "
                f"'{completed_status}'. Current status: '{target.status}'."
            )

        data['_target'] = target
        data['_model'] = model
        return data