import random

DIGITS = "0123456789"


def get_otp(length=6):
    """
    Returns an variable length OTP generated at random
    """
    otp = "".join(random.choices(DIGITS, k=length))
    return otp
