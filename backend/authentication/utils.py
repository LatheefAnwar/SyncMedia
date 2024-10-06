from django.core.mail import send_mail
from django.conf import settings
import random
import string


def send_email_otp(email, otp):
    subject = 'Registration OTP'
    message = f'OTP is: {otp} '
    from_email = settings.EMAIL_HOST_USER
    receipient_list = [email]
    send_mail(
        subject = subject,
        message= message,
        from_email= from_email,
        recipient_list= receipient_list,
        fail_silently=False,
    )




def otp_generator(length=6):
    strings = string.digits
    otp = "".join(random.choice(strings) for _ in range(length))
    return str(otp)