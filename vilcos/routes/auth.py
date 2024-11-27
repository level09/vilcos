from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from vilcos.models import User
from vilcos.db import AsyncSessionMaker
from vilcos.auth_utils import login_required, login_user, logout_user, get_current_user
from vilcos.utils import get_root_path
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))

@router.get("/signin")
async def signin_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("auth/signin.html", {"request": request})

@router.get("/signup")
async def signup_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.post("/signin")
async def signin(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return JSONResponse(
            content={"success": False, "message": "Email and password required"},
            status_code=400
        )
    
    async with AsyncSessionMaker() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not User.verify_password(password, user.password_hash):
            return JSONResponse(
                content={"success": False, "message": "Invalid email or password"},
                status_code=400
            )
        
        login_user(request, user)
        return JSONResponse(
            content={"success": True, "message": "Login successful", "redirect": "/dashboard"}
        )

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    
    if not all([email, password, username]):
        return JSONResponse(
            content={"success": False, "message": "All fields are required"},
            status_code=400
        )
    
    async with AsyncSessionMaker() as session:
        # Check if user exists
        result = await session.execute(
            select(User).where(
                (User.email == email) | (User.username == username)
            )
        )
        if result.scalar_one_or_none():
            return JSONResponse(
                content={"success": False, "message": "Email or username already exists"},
                status_code=400
            )
        
        # Create new user
        user = User(
            email=email,
            username=username,
            password_hash=User.get_password_hash(password)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        login_user(request, user)
        return JSONResponse(
            content={"success": True, "message": "Account created successfully", "redirect": "/dashboard"}
        )

@router.get("/signout")
async def signout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/auth/signin")

@router.get("/me")
async def get_user(request: Request):
    """Get current user information."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin
    }
