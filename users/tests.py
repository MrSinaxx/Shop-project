from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser
from .utils import generate_otp


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = "/api/users/register/"
        self.login_url = "/api/users/login/"
        self.otp_verification_url = "/api/users/verify-otp/"
        self.valid_registration_data = {
            "phone_number": "1234567890",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_registration_valid_data(self):
        response = self.client.post(
            self.registration_url, self.valid_registration_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
