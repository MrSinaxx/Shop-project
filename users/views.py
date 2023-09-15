from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .utils import generate_otp
from .serializers import CustomUserSerializer, OTPSerializer


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        user = CustomUser.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        otp = generate_otp()

        return Response(
            {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
        )

