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
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        data['user'] = user
        return data


# ---------------------------------------------------------------------
# GS-REG-103: Role-specific registration serializers
# ---------------------------------------------------------------------
from .models import VillageCity


class BaseRoleRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    village_city = serializers.PrimaryKeyRelatedField(
        queryset=VillageCity.objects.all(), required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'ward_number', 'village_city']

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value


class CitizenRegistrationSerializer(BaseRoleRegistrationSerializer):

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            ward_number=validated_data.get('ward_number', ''),
            village_city=validated_data['village_city'],
            role='citizen',
            approval_status='approved',
        )


class StaffRegistrationSerializer(BaseRoleRegistrationSerializer):
    identity_document = serializers.FileField(required=True)

    class Meta(BaseRoleRegistrationSerializer.Meta):
        fields = BaseRoleRegistrationSerializer.Meta.fields + ['identity_document']

    def create(self, validated_data):
        village_city = validated_data['village_city']
        # Auto-link to an approved Sarpanch in the same village/city, if one exists yet.
        supervisor = User.objects.filter(
            role='sarpanch',
            approval_status='approved',
            village_city=village_city,
        ).first()

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            ward_number=validated_data.get('ward_number', ''),
            village_city=village_city,
            identity_document=validated_data['identity_document'],
            role='staff',
            approval_status='pending',
        )
        if supervisor:
            user.supervisor = supervisor
            user.save(update_fields=['supervisor'])
        return user


class SarpanchRegistrationSerializer(BaseRoleRegistrationSerializer):
    identity_document = serializers.FileField(required=True)

    class Meta(BaseRoleRegistrationSerializer.Meta):
        fields = BaseRoleRegistrationSerializer.Meta.fields + ['identity_document']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            ward_number=validated_data.get('ward_number', ''),
            village_city=validated_data['village_city'],
            identity_document=validated_data['identity_document'],
            role='sarpanch',
            approval_status='pending',
        )


# ---------------------------------------------------------------------
# GS-REG-104: Read-only serializers for cascading location dropdowns
# ---------------------------------------------------------------------
from .models import District, Taluka, VillageCity


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'lgd_code']


class TalukaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taluka
        fields = ['id', 'name', 'lgd_code', 'district_id']


class VillageCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VillageCity
        fields = ['id', 'name', 'lgd_code', 'taluka_id']
