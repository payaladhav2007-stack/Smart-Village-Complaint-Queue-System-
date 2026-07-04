from rest_framework import serializers
from .models import Complaint, GOVERNMENT_SUB_CHOICES, PERSONAL_SUB_CHOICES


VALID_GOVERNMENT_SUBS = [choice[0] for choice in GOVERNMENT_SUB_CHOICES]
VALID_PERSONAL_SUBS = [choice[0] for choice in PERSONAL_SUB_CHOICES]


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id',
            'main_category',
            'sub_category',
            'complaint_subject',
            'description',
            'media_path',
            'latitude',
            'longitude',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        main_category = data.get('main_category', 'government')
        sub_category = data.get('sub_category', '')
        complaint_subject = data.get('complaint_subject', '')

        if main_category == 'government':
            if not sub_category:
                raise serializers.ValidationError(
                    "sub_category is required for Government Services."
                )
            if sub_category not in VALID_GOVERNMENT_SUBS:
                raise serializers.ValidationError(
                    f"Invalid sub_category for Government. Must be one of: {', '.join(VALID_GOVERNMENT_SUBS)}"
                )

        elif main_category == 'personal':
            if not sub_category:
                raise serializers.ValidationError(
                    "sub_category is required for Personal Issues."
                )
            if sub_category not in VALID_PERSONAL_SUBS:
                raise serializers.ValidationError(
                    f"Invalid sub_category for Personal. Must be one of: {', '.join(VALID_PERSONAL_SUBS)}"
                )
            if not complaint_subject:
                raise serializers.ValidationError(
                    "complaint_subject is required for Personal Issues."
                )

        elif main_category == 'other':
            if not complaint_subject:
                raise serializers.ValidationError(
                    "complaint_subject is required for Other category."
                )

        return data

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters long."
            )
        return value

    def validate_latitude(self, value):
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError(
                    "Latitude must be between -90 and 90."
                )
        return value

    def validate_longitude(self, value):
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError(
                    "Longitude must be between -180 and 180."
                )
        return value
