from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import CitizenRegistrationSerializer, StaffRegistrationSerializer, SarpanchRegistrationSerializer
from .serializers import DistrictSerializer, TalukaSerializer, VillageCitySerializer
from .models import District, Taluka, VillageCity
from .models import User
from .serializers import PendingStaffSerializer
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
def register_landing(request):
    return render(request, 'accounts/register_landing.html')

def register_citizen_page(request):
    return render(request, 'accounts/register_citizen.html')

def register_staff_page(request):
    return render(request, 'accounts/register_staff.html')

def register_sarpanch_page(request):
    return render(request, 'accounts/register_sarpanch.html')
# ---------------------------------------------------------------------
# GS-REG-108: OTP Login for Sarpanch/Nagarsevak
# ---------------------------------------------------------------------
import random
from datetime import timedelta
from django.utils import timezone
from sms_auth.models import SmsOtp

class SarpanchPasswordCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'success': False, 'message': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'success': False, 'message': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user.role != 'sarpanch':
            return Response(
                {'success': False, 'message': 'This login flow is for Sarpanch/Nagarsevak accounts only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.approval_status != 'approved':
            return Response(
                {'success': False, 'message': 'Your account is not yet approved. Please contact the administrator.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.phone_number:
            return Response(
                {'success': False, 'message': 'No phone number linked to this account. Contact administrator.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_code = str(random.randint(100000, 999999))
        SmsOtp.objects.create(
            phone_number=user.phone_number,
            code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=7),
        )

        print(f"[GS-REG-108] OTP for Sarpanch {username} ({user.phone_number}): {otp_code}")

        return Response({
            'success': True,
            'message': 'OTP sent to your registered mobile number.',
            'phone_number': user.phone_number[:4] + '******',
            'username': username,
        }, status=status.HTTP_200_OK)


class SarpanchOTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        otp_code = request.data.get('otp_code', '').strip()

        if not username or not otp_code:
            return Response(
                {'success': False, 'message': 'Username and OTP code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(username=username, role='sarpanch')
        except User.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Invalid request.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.phone_number:
            return Response(
                {'success': False, 'message': 'No phone number linked to this account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = SmsOtp.objects.filter(
            phone_number=user.phone_number,
            is_used=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid(otp_code):
            return Response(
                {'success': False, 'message': 'Invalid or expired OTP. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp.is_used = True
        otp.save()

        login(request, user)

        return Response({
            'success': True,
            'message': 'Login successful.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'role': user.role,
                'village_city': user.village_city_id,
            }
        }, status=status.HTTP_200_OK)


class SarpanchOTPResendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()

        if not username:
            return Response(
                {'success': False, 'message': 'Username is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(username=username, role='sarpanch')
        except User.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Invalid request.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.phone_number:
            return Response(
                {'success': False, 'message': 'No phone number linked to this account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        SmsOtp.objects.filter(
            phone_number=user.phone_number,
            is_used=False
        ).update(is_used=True)

        otp_code = str(random.randint(100000, 999999))
        SmsOtp.objects.create(
            phone_number=user.phone_number,
            code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=7),
        )

        print(f"[GS-REG-108] RESENT OTP for Sarpanch {username} ({user.phone_number}): {otp_code}")

        return Response({
            'success': True,
            'message': 'A new OTP has been sent to your registered mobile number.',
        }, status=status.HTTP_200_OK)


def sarpanch_login_page(request):
    return render(request, 'accounts/sarpanch_login.html')


# ---------------------------------------------------------------------
# GS-REG-107: Sarpanch dashboard — approve/reject pending Staff
# ---------------------------------------------------------------------
class PendingStaffListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'sarpanch':
            return Response({"error": "Only Sarpanch/Nagarsevak accounts can access this."}, status=status.HTTP_403_FORBIDDEN)

        pending_staff = User.objects.filter(
            role='staff',
            approval_status='pending',
            village_city=user.village_city
        ).order_by('username')

        serializer = PendingStaffSerializer(pending_staff, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApproveStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        sarpanch = request.user
        if sarpanch.role != 'sarpanch':
            return Response({"error": "Only Sarpanch/Nagarsevak accounts can approve Staff."}, status=status.HTTP_403_FORBIDDEN)

        try:
            staff_user = User.objects.get(id=user_id, role='staff', village_city=sarpanch.village_city)
        except User.DoesNotExist:
            return Response({"error": "Staff registration not found in your area."}, status=status.HTTP_404_NOT_FOUND)

        staff_user.approval_status = 'approved'
        staff_user.approved_by = sarpanch
        staff_user.supervisor = sarpanch
        staff_user.save(update_fields=['approval_status', 'approved_by', 'supervisor'])

        return Response({
            "success": True,
            "message": f"{staff_user.username} approved successfully.",
            "approval_status": staff_user.approval_status
        }, status=status.HTTP_200_OK)


class RejectStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        sarpanch = request.user
        if sarpanch.role != 'sarpanch':
            return Response({"error": "Only Sarpanch/Nagarsevak accounts can reject Staff."}, status=status.HTTP_403_FORBIDDEN)

        try:
            staff_user = User.objects.get(id=user_id, role='staff', village_city=sarpanch.village_city)
        except User.DoesNotExist:
            return Response({"error": "Staff registration not found in your area."}, status=status.HTTP_404_NOT_FOUND)

        staff_user.approval_status = 'rejected'
        staff_user.approved_by = sarpanch
        staff_user.save(update_fields=['approval_status', 'approved_by'])

        return Response({
            "success": True,
            "message": f"{staff_user.username} rejected.",
            "approval_status": staff_user.approval_status
        }, status=status.HTTP_200_OK)