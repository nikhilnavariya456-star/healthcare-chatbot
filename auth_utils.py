from fastapi import Request, HTTPException
from jose import jwt, JWTError
from database import SessionLocal
from models import User
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGO = os.getenv("JWT_ALGORITHM")

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db = SessionLocal()
    user = db.query(User).get(int(user_id))
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user