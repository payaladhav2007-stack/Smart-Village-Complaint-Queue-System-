from django.urls import path
from .views import RegisterView, LoginView, LogoutView, register_page, login_page

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-page/', register_page, name='register-page'),
    path('login-page/', login_page, name='login-page'),
]
