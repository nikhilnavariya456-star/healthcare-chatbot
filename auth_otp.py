# auth_otp.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
import random
from datetime import datetime, timedelta
from jose import jwt
import os

from email_utils import send_otp_email

router = APIRouter(prefix="/auth/otp")

OTP_STORE = {}

# ---------------------------
# REQUEST OTP
# ---------------------------
@router.post("/request")
def request_otp(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    # ❌ User does not exist
    if not user:
        return RedirectResponse(
            "/?error=login_with_google_first",
            302
        )

    # ❌ User never logged with Google
    if not user.google_verified:
        return RedirectResponse(
            "/?error=login_with_google_first",
            302
        )

    otp = str(random.randint(100000, 999999))

    OTP_STORE[email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }

    send_otp_email(email, otp)

    return RedirectResponse(f"/verify-otp?email={email}", 302)

# ---------------------------
# VERIFY OTP
# ---------------------------
@router.post("/verify")
def verify_otp(
    email: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db)
):
    data = OTP_STORE.get(email)

    if not data or data["expires"] < datetime.utcnow():
        return RedirectResponse(
            f"/verify-otp?error=expired&email={email}", 302
        )

    if data["otp"] != otp:
        return RedirectResponse(
            f"/verify-otp?error=invalid&email={email}", 302
        )

    user = db.query(User).filter(User.email == email).first()

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "provider": "otp",
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    token = jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )

    OTP_STORE.pop(email, None)

    response = RedirectResponse("/chat-ui", 302)
    response.set_cookie("access_token", token, httponly=True)
    return response