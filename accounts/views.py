from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import CitizenRegistrationSerializer, StaffRegistrationSerializer, SarpanchRegistrationSerializer
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
