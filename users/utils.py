import random


def generate_otp():
    otp = random.randint(1000, 9999)
    print(f"Your OTP is: {otp}")
    return otp
