from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import Account, OTP
from .serializers import *
from .utility import generate_otp, send_otp_email
from .throttles import OTPThrottle


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='signup/regular')
    def signup_regular(self, request):
        serializer = RegularUserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to your email."})
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='signup/merchant')
    def signup_merchant(self, request):
        serializer = MerchantSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to your email."})
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='verify-email')
    def verify_email(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = Account.objects.get(email=serializer.validated_data['email'])
                otp = OTP.objects.filter(user=user, code=serializer.validated_data['code']).last()
                if otp and not otp.is_expired():
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    otp.delete()
                    return Response({"message": "Email verified successfully"})
                return Response({"error": "Invalid or expired OTP"}, status=400)
            except Account.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='resend-otp', throttle_classes=[OTPThrottle])
    def resend_otp(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = Account.objects.get(email=serializer.validated_data['email'])
                otp = generate_otp()
                OTP.objects.create(user=user, code=otp)
                send_otp_email(user.email, otp)
                return Response({"message": "OTP resent"})
            except Account.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        user = authenticate(username=request.data.get('email'), password=request.data.get('password'))
        if user and user.is_verified:
            refresh = RefreshToken.for_user(user)
            return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})
        return Response({"error": "Invalid credentials or not verified"}, status=400)

    @action(detail=False, methods=['post'], url_path='password-reset/request')
    def password_reset_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = Account.objects.get(email=serializer.validated_data['email'])
                otp = generate_otp()
                OTP.objects.create(user=user, code=otp)
                send_otp_email(user.email, otp)
                return Response({"message": "Password reset OTP sent"})
            except Account.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='password-reset/confirm')
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = Account.objects.get(email=serializer.validated_data['email'])
                otp = OTP.objects.filter(user=user, code=serializer.validated_data['code']).last()
                if otp and not otp.is_expired():
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    otp.delete()
                    return Response({"message": "Password has been reset."})
                return Response({"error": "Invalid or expired OTP"}, status=400)
            except Account.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='upgrade-to-merchant', permission_classes=[IsAuthenticated])
    def upgrade_to_merchant(self, request):
        if request.user.user_type == 'merchant':
            return Response({"error": "You are already a merchant."}, status=400)

        serializer = UpgradeToMerchantSerializer(data=request.data)
        if serializer.is_valid():
            request.user.user_type = 'merchant'
            request.user.save()
            MerchantProfile.objects.create(
                user=request.user,
                company_name=serializer.validated_data['company_name'],
                business_license=serializer.validated_data['business_license']
            )
            return Response({"message": "Account upgraded to merchant."})
        return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['get'], url_path='profile', permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        serializer = AccountSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
