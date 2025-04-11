import random
import string
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from decouple import config
from twilio.rest import Client

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your OTP for Verification"
    message = f"Your OTP is {otp}. It will expire in 10 minutes."
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])

def send_otp_sms(phone_number, otp):
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_ACCOUNT_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP for password reset is {otp}. It is valid for 10 minutes.",
        from_="your_twilio_number",
        to=phone_number
    )
    return message.sid


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    random_string = ''.join(random.choices(characters, k=length))
    return random_string

# The send email function
def send_email(email, html_message, mail_subject,):
    try:
        email = EmailMessage(
            mail_subject,
            html_message,
            to=[email]
        )
        email.content_subtype = "html"
        email.send()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
    