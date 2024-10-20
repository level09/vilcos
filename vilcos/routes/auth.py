# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from vilcos.config import Settings
from gotrue.errors import AuthApiError

router = APIRouter()
settings = Settings()
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
templates = Jinja2Templates(directory="vilcos/templates")


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
        return JSONResponse(
            content={
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "role": response.user.role,
                    "last_sign_in_at": response.user.last_sign_in_at,
                },
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signup")
async def signup(request: Request):

    data = await request.json()
    try:
        response = supabase.auth.sign_up(
            credentials={
                "email": data.get("email"),
                "password": data.get("password"),
                "options": {"data": {"username": data.get("username")}},
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


# Add more auth routes as needed (forgot password, OAuth, etc.)
