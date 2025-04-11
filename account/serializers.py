from rest_framework import serializers
from .models import Account, MerchantProfile, OTP
from .utility import generate_otp, send_otp_email


class RegularUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        validated_data['user_type'] = 'regular'
        validated_data['is_active'] = False
        user = Account.objects.create_user(**validated_data)
        otp = generate_otp()
        OTP.objects.create(user=user, code=otp)
        send_otp_email(user.email, otp)
        return user


class MerchantSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField()
    business_license = serializers.CharField()

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'company_name', 'business_license']

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        business_license = validated_data.pop('business_license')

        validated_data['user_type'] = 'merchant'
        validated_data['is_active'] = False

        user = Account.objects.create_user(**validated_data)
        MerchantProfile.objects.create(user=user, company_name=company_name, business_license=business_license)

        otp = generate_otp()
        OTP.objects.create(user=user, code=otp)
        send_otp_email(user.email, otp)
        return user


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField()


class UpgradeToMerchantSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    business_license = serializers.CharField()

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['id', 'email','username','first_name', 'last_name', 'phone_number', 'profile_image', 'user_type']
        read_only_fields = ['id', 'email_verified', 'phone_verified']
