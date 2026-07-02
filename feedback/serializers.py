from rest_framework import serializers
from grievances.models import Complaint
from appointments.models import Appointment


class FeedbackSubmitSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(
        choices=['grievance', 'appointment'],
        required=False,
        default='grievance'
    )
    target_id = serializers.IntegerField(required=False, default=1)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    category_ratings = serializers.DictField(required=False, default=dict)
    tags = serializers.ListField(required=False, default=list)
    is_anonymous = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        target_type = data.get('target_type', 'grievance')
        target_id = data.get('target_id', 1)

        model = Complaint if target_type == 'grievance' else Appointment
        completed_status = 'resolved' if target_type == 'grievance' else 'completed'

        try:
            target = model.objects.get(id=target_id)
        except model.DoesNotExist:
            # Don't fail if no target specified — just skip status check
            data['_target'] = None
            data['_model'] = model
            return data

        if target.status != completed_status:
            # For form submissions without specific target, skip status check
            if not data.get('target_id'):
                data['_target'] = None
                data['_model'] = model
                return data

        data['_target'] = target
        data['_model'] = model
        return data
