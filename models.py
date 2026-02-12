from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 🔥 VERY IMPORTANT FLAG
    google_verified = Column(Boolean, default=False)

    name = Column(String(100), nullable=True)

    email = Column(String(150), unique=True, index=True, nullable=False)

    password_hash = Column(String(255), nullable=True)

    # local | google
    auth_provider = Column(String(50), default="local", nullable=False)

    profile_pic = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)