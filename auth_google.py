# auth_google.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from database import SessionLocal
from models import User
import os
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()
oauth = OAuth()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGO = os.getenv("JWT_ALGORITHM")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise RuntimeError("Google OAuth env vars missing")

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ---------------------------
# GOOGLE LOGIN
# ---------------------------
@router.get("/auth/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(
        request,
        GOOGLE_REDIRECT_URI
    )

# ---------------------------
# GOOGLE CALLBACK
# ---------------------------
@router.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo", {})

    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Google login failed")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # 🆕 FIRST TIME GOOGLE LOGIN
            user = User(
                email=email,
                name=name,
                profile_pic=picture,
                auth_provider="google",
                google_verified=True   # 🔥 VERY IMPORTANT
            )
            db.add(user)
        else:
            # 🔁 ALREADY EXISTS → ENSURE GOOGLE VERIFIED
            user.name = name
            user.profile_pic = picture
            user.auth_provider = "google"
            user.google_verified = True  # 🔥 VERY IMPORTANT

        db.commit()
        db.refresh(user)
    finally:
        db.close()

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "provider": "google",
        "exp": datetime.utcnow() + timedelta(days=7),
    }

    access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    response = RedirectResponse("/chat-ui", 302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response