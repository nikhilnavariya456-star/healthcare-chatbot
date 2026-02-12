# otp_store.py
from datetime import datetime, timedelta
import random

otp_store = {}

def generate_otp(email: str):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }
    return otp

def verify_otp(email: str, otp: str):
    data = otp_store.get(email)
    if not data:
        return False
    if datetime.utcnow() > data["expires"]:
        return False
    return data["otp"] == otp