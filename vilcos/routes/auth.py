# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from vilcos.config import Settings

router = APIRouter()
settings = Settings()
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
templates = Jinja2Templates(directory="app/templates")

@router.post("/signin")
async def signin(request: Request):
    data = await request.json()
    try:
        response = supabase.auth.sign_in_with_password(
            credentials={"email": data.get('email'), "password": data.get('password')}
        )
        return JSONResponse(content={
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_at": response.session.expires_at,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "role": response.user.role,
                "last_sign_in_at": response.user.last_sign_in_at
            }
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()
    try:
        response = supabase.auth.sign_up(
            credentials={
                "email": data.get('email'),
                "password": data.get('password'),
                "options": {"data": {"username": data.get('username')}}
            }
        )
        return JSONResponse(content={
            "success": True,
            "message": "Please check your email to verify your account."
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signout")
async def signout(request: Request):
    try:
        supabase.auth.sign_out()
        return JSONResponse(content={"success": True, "message": "Signed out successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback")
async def callback(request: Request):
    return templates.TemplateResponse("auth/callback.html", {"request": request})

# Add more auth routes as needed (forgot password, OAuth, etc.)