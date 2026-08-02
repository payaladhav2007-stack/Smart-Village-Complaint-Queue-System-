from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    posted_by_username = serializers.CharField(
        source='posted_by.username', read_only=True
    )
    posted_by_role = serializers.CharField(
        source='posted_by.role', read_only=True
    )
    village_city_name = serializers.CharField(
        source='village_city.name', read_only=True
    )

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content',
            'posted_by', 'posted_by_username', 'posted_by_role',
            'village_city', 'village_city_name',
            'is_pinned', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'posted_by', 'village_city',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['posted_by'] = user
        validated_data['village_city'] = user.village_city
        return super().create(validated_data)


class NoticeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_pinned']