# email_utils.py
import smtplib
from email.message import EmailMessage
import os

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Login OTP – Healthcare Assistant"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg.set_content(f"""
Your OTP is: {otp}

This OTP is valid for 5 minutes.
If you didn’t request this, ignore this email.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)