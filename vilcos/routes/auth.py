from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from vilcos.models import User, Role
from vilcos.db import get_db
from vilcos.utils import get_root_path
from vilcos.auth_utils import get_current_user, login_user, logout_user
from vilcos.config import settings
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))

# Password hasher instance
ph = PasswordHasher()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.get("/signup")
async def signup_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        # Check if email already exists
        result = await db.execute(select(User).filter(User.email == data.email))
        if result.scalar_one_or_none():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Email already registered"}
            )
        
        # Check if username exists
        result = await db.execute(select(User).filter(User.username == data.username))
        if result.scalar_one_or_none():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Username already taken"}
            )
        
        # Get default user role
        result = await db.execute(select(Role).filter(Role.name == "user"))
        default_role = result.scalar_one_or_none()
        if not default_role:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Default role not found"}
            )
        
        # Create new user with hashed password and default role
        user = User(
            email=data.email,
            username=data.username,
            password=User.get_password_hash(data.password),
            roles=[default_role]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Log the user in
        login_user(request, user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "User created successfully"}
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e) if settings.debug else "An error occurred while creating your account"}
        )

@router.get("/signin")
async def signin_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("auth/signin.html", {"request": request})

@router.post("/signin")
async def signin(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        # Find user by email
        result = await db.execute(select(User).filter(User.email == data.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not User.verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Log the user in
        login_user(request, user)
        return JSONResponse(content={"message": "Logged in successfully"})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e) if settings.debug else "An error occurred while signing in"}
        )

@router.post("/signout")
async def signout(request: Request):
    logout_user(request)
    return {"message": "Successfully signed out"}
