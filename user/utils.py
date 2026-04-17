import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def generate_random_password(min_length=8, max_length=12) -> str:
    """Generates a secure random password with a mix of upper, lower, digits, and special characters."""
    char_set = (
        string.ascii_uppercase
        + string.ascii_lowercase
        + string.digits
        + string.punctuation
    )
    password_length = random.randint(min_length, max_length)

    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    # Fill the remaining characters
    password += [random.choice(char_set) for _ in range(password_length - 4)]
    random.shuffle(password)

    return "".join(password)


def generate_otp():
    return str(random.randint(100000, 999999))



# Send OTP to user's email for verification
def send_otp(user):
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    send_mail(
        subject="Verify your account",
        message=f"Your OTP is {otp}. It expires in 1 minute.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )