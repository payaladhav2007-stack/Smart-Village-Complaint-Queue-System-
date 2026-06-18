from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'ward_number']

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_ward_number(self, value):
        if not value:
            raise serializers.ValidationError("Ward number is required.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            ward_number=validated_data['ward_number'],
            role='citizen'
        )
        return user
