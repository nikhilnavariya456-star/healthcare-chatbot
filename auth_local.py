from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from security import hash_password, verify_password
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "secret")
JWT_ALGO = os.getenv("JWT_ALGORITHM", "HS256")


# 🔐 LOGIN PAGE (GET)
@router.get("/local-login", response_class=HTMLResponse)
def local_login_page(request: Request):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse(
        "local_login.html",
        {"request": request}
    )


# 📝 REGISTER (POST)
@router.post("/auth/local/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return RedirectResponse("/register?error=exists", status_code=302)

    new_user = User(
        email=email,
        password_hash=hash_password(password),
        auth_provider="local"
    )
    db.add(new_user)
    db.commit()

    # ✅ success message ke sath login page
    return RedirectResponse("/local-login?success=1", status_code=302)


# 🔐 LOGIN (POST)
@router.post("/auth/local/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.password_hash:
        return RedirectResponse("/local-login?error=1", status_code=302)

    if not verify_password(password, user.password_hash):
        return RedirectResponse("/local-login?error=1", status_code=302)

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "provider": "local",
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    response = RedirectResponse("/chat-ui", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response