from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db import models
import datetime
import random

# This is the folder where profile images are stored
def upload_location(instance, filename):
    file_path = "profile_image/{user_id}/{image}".format(
        user_id=str(instance.id), image=filename
    )
    return file_path

class AccountManager(BaseUserManager): 
    use_in_migrations = True
    def create_user(self, email, password=None, **extra_fields):
        if email is None:
            raise TypeError('User should have an Email')
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Account(AbstractUser):
    USER_TYPE_CHOICES = (
        ('regular', 'Regular User'),
        ('merchant', 'Merchant'),
    )
    email = models.EmailField(verbose_name="email", unique=True)
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    is_active = models.BooleanField(default=False)  # Account is inactive until OTP is verified
    is_verified = models.BooleanField(default=False)  # Email verification
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email_otp = models.CharField(max_length=6, blank=True, null=True)  # Store OTP for activation

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate a 6-digit OTP for email verification"""
        self.otp = str(random.randint(100000, 999999))
        self.save()

    

class OTP(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=10)

class MerchantProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='merchant_profile')
    company_name = models.CharField(max_length=100)
    business_license = models.CharField(max_length=50)

    def __str__(self):
        return self.user.email

