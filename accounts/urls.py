from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, LoginView, LogoutView, register_page, login_page, register_landing, register_citizen_page, register_staff_page, register_sarpanch_page
from .views import CitizenRegistrationView, StaffRegistrationView, SarpanchRegistrationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-page/', register_page, name='register-page'),
    path('login-page/', login_page, name='login-page'),
    path('token/', obtain_auth_token, name='api-token'),
    path('register/citizen/', CitizenRegistrationView.as_view(), name='register-citizen'),
    path('register/staff/', StaffRegistrationView.as_view(), name='register-staff'),
    path('register/sarpanch/', SarpanchRegistrationView.as_view(), name='register-sarpanch'),
    path('register-landing/', register_landing, name='register-landing'),
    path('register-citizen-page/', register_citizen_page, name='register-citizen-page'),
    path('register-staff-page/', register_staff_page, name='register-staff-page'),
    path('register-sarpanch-page/', register_sarpanch_page, name='register-sarpanch-page'),
]