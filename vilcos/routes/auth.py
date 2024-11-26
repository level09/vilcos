# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from vilcos.config import Settings
from gotrue.errors import AuthApiError
from datetime import datetime
from vilcos.dependencies import login_required
from vilcos.utils import get_root_path
import os

router = APIRouter()
settings = Settings()
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))


@router.get("/signin")
async def signin_page(request: Request):
    return templates.TemplateResponse("auth/signin.html", {"request": request})


@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@router.get("/signout")
async def signout_page(request: Request):
    return templates.TemplateResponse("auth/signout.html", {"request": request})


@router.get("/forgot-password")
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("auth/forgot-password.html", {"request": request})


@router.get("/signin/github")
async def signin_with_github(request: Request):
    resp = supabase.auth.sign_in_with_oauth(
        {
            "provider": "github",
            "options": {"redirect_to": f"{request.url_for('callback')}"},
        }
    )
    return RedirectResponse(url=resp.url)


@router.post("/signin")
async def signin(request: Request):
    data = await request.json()
    try:
        response = supabase.auth.sign_in_with_password(
            credentials={"email": data.get("email"), "password": data.get("password")}
        )
        
        # Convert the expiration timestamp to a datetime object and then to ISO 8601 string
        expires_at = datetime.fromtimestamp(response.session.expires_at).isoformat() if response.session.expires_at else None
        
        # Set user session using Starlette's session middleware
        request.session['user'] = {
            'access_token': response.session.access_token,
            'refresh_token': response.session.refresh_token,
            'expires_at': expires_at,  # Store as ISO 8601 string
            'user': {
                'id': response.user.id,
                'email': response.user.email,
                'role': response.user.role,
                'last_sign_in_at': response.user.last_sign_in_at.isoformat() if response.user.last_sign_in_at else None,
            }
        }
        return JSONResponse(
            content={"success": True, "message": "Login successful", "redirect": "/dashboard"}
        )
    except AuthApiError as e:
        return JSONResponse(
            content={"success": False, "message": str(e)},
            status_code=400
        )

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()
    try:
        response = supabase.auth.sign_up(
            credentials={
                "email": data.get("email"),
                "password": data.get("password"),
                "options": {
                    "data": {"username": data.get("username")},
                    "email_redirect_to": f"{request.url_for('signin_page')}",  # Redirect to the signin page
                },
            }
        )

        return JSONResponse(
            content={
                "success": True,
                "message": "Please check your email to verify your account.",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signout")
async def signout(request: Request):
    try:
        supabase.auth.sign_out()
        return JSONResponse(
            content={"success": True, "message": "Signed out successfully"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback")
async def callback(request: Request):
    return templates.TemplateResponse("auth/callback.html", {"request": request})


@router.post("/process-tokens")
async def process_tokens(request: Request):
    data = await request.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    if access_token and refresh_token:
        # Fetch the user information using the access token
        try:
            user_info = supabase.auth.get_user(access_token)
            if user_info.user is None:  # Check if user_info.user exists
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Failed to retrieve user info",
                    },
                    status_code=400,
                )

            # Set session data
            request.session["user"] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_info.user,
            }

            return JSONResponse(content={"success": True, "redirect": "/dashboard"})
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": str(e)}, status_code=400
            )

    return JSONResponse(
        content={"success": False, "message": "Missing token data"}, status_code=400
    )

@router.get("/protected")
async def protected_route(user: dict = Depends(login_required)):
    return {"message": "This is a protected route", "user": user}
