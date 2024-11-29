from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from vilcos.db import Base
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize the password hasher with secure defaults
ph = PasswordHasher()

# Association table for User-Role many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # Updated relationship to many-to-many
    users = relationship("User", secondary=user_roles, back_populates="roles")

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    
    # Updated relationship to many-to-many
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")

    _admin_role = None

    @property
    def is_authenticated(self):
        return True

    @property
    def role_names(self):
        """Get list of role names."""
        return [role.name for role in self.roles]

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role using eager loaded roles."""
        return "admin" in self.role_names

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> "User":
        """Get user by ID with roles preloaded."""
        result = await db.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> "User":
        """Get user by email with roles preloaded."""
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str) -> "User":
        """Get user by username with roles preloaded."""
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar_one_or_none()

    @classmethod
    async def email_exists(cls, db: AsyncSession, email: str, exclude_id: int = None) -> bool:
        """Check if email exists, optionally excluding a user ID."""
        query = select(cls).where(cls.email == email)
        if exclude_id is not None:
            query = query.where(cls.id != exclude_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def username_exists(cls, db: AsyncSession, username: str, exclude_id: int = None) -> bool:
        """Check if username exists, optionally excluding a user ID."""
        query = select(cls).where(cls.username == username)
        if exclude_id is not None:
            query = query.where(cls.id != exclude_id)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return ph.hash(password)

    @classmethod
    async def get_admin_count(cls, db: AsyncSession) -> int:
        """Get count of admin users."""
        result = await db.execute(
            select(cls)
            .join(user_roles)
            .join(Role)
            .where(Role.name == "admin")
        )
        return len(result.scalars().all())
