from sqlalchemy import Column, Integer, DateTime, Boolean, String
from sqlalchemy.sql import func
from vilcos.db import Base
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Initialize the password hasher with secure defaults
ph = PasswordHasher()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    @property
    def is_authenticated(self):
        return True

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return ph.hash(password)
