from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import CitizenRegistrationSerializer, StaffRegistrationSerializer, SarpanchRegistrationSerializer
from .serializers import DistrictSerializer, TalukaSerializer, VillageCitySerializer
from .models import District, Taluka, VillageCity
from rest_framework.parsers import MultiPartParser, FormParser

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Citizen registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "ward_number": user.ward_number,
                    "role": user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "ward_number": user.ward_number,
                    "role": user.role,
                    "is_staff": user.is_staff
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({
            "message": "Logged out successfully."
        }, status=status.HTTP_200_OK)
def register_page(request):
    return render(request, 'accounts/register.html')

def login_page(request):
    return render(request, 'accounts/login.html')


# ---------------------------------------------------------------------
# GS-REG-103: Role-specific registration views
# ---------------------------------------------------------------------
class CitizenRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CitizenRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Registration successful. You can log in now.",
                "approval_status": user.approval_status,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "village_city": user.village_city_id,
                }
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StaffRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = StaffRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Registration submitted. Awaiting Sarpanch approval.",
                "approval_status": user.approval_status,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "village_city": user.village_city_id,
                    "supervisor": user.supervisor_id,
                }
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SarpanchRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = SarpanchRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Registration submitted. Awaiting Django Admin approval.",
                "approval_status": user.approval_status,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "village_city": user.village_city_id,
                }
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------
# GS-REG-104: Cascading location dropdown APIs (read-only)
# ---------------------------------------------------------------------
class DistrictListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        districts = District.objects.all().order_by('name')
        return Response(DistrictSerializer(districts, many=True).data, status=status.HTTP_200_OK)


class TalukaListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        district_id = request.query_params.get('district_id')
        if not district_id:
            return Response(
                {"error": "district_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        talukas = Taluka.objects.filter(district_id=district_id).order_by('name')
        return Response(TalukaSerializer(talukas, many=True).data, status=status.HTTP_200_OK)


class VillageCityListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        district_id = request.query_params.get('district_id')
        taluka_id = request.query_params.get('taluka_id')
        if not district_id or not taluka_id:
            return Response(
                {"error": "Both district_id and taluka_id query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        villages = VillageCity.objects.filter(
            taluka_id=taluka_id,
            taluka__district_id=district_id
        ).order_by('name')
        return Response(VillageCitySerializer(villages, many=True).data, status=status.HTTP_200_OK)
