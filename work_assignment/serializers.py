from rest_framework import serializers
from .models import WorkAssignment
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAssignment
        fields = [
            'id', 'assigned_to', 'title', 'description',
            'related_complaint', 'status', 'due_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status']

    def validate_assigned_to(self, value):
        request = self.context['request']
        # Staff must be in same village_city as the sarpanch
        if value.role != 'staff':
            raise serializers.ValidationError("You can only assign tasks to Staff/Officers.")
        if value.approval_status != 'approved':
            raise serializers.ValidationError("This staff member is not yet approved.")
        if value.village_city != request.user.village_city:
            raise serializers.ValidationError(
                "You can only assign tasks to Staff in your own village/city."
            )
        return value

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkAssignmentListSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    village_city_name = serializers.CharField(
        source='assigned_by.village_city.name', read_only=True
    )

    class Meta:
        model = WorkAssignment
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'assigned_by_name', 'assigned_to_name', 'village_city_name',
            'related_complaint', 'created_at', 'updated_at'
        ]


class WorkAssignmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAssignment
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in ['pending', 'in_progress', 'completed']:
            raise serializers.ValidationError("Invalid status.")
        return value