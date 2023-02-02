import random
from datetime import datetime
from uuid import uuid4

DIGITS = "0123456789"


def generate_otp(length=6):
    """
    Returns an random variable length OTP
    """
    otp = "".join(random.choices(DIGITS, k=length))
    return otp


def generate_random_filename(ext):
    """Generates a random filename based on time"""
    return uuid4().hex + "_" + str(datetime.now()).replace(" ", "_") + ext
