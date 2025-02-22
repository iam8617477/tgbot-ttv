import random

from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    otp = random.randint(100000, 999999)
    return str(otp)


def send_email_verification(email):
    otp = generate_otp()
    send_otp_to_email(email, otp)


def send_otp_to_email(email, otp):
    subject = 'Email Verification OTP'
    message = f'Your OTP code is: {otp}. It will expire in 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])
