# users/urls.py
from django.urls import path
from .views import UserRegistrationView, UserLoginView, OTPVerificationView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("verify-otp/", OTPVerificationView.as_view(), name="verify-otp"),
]
