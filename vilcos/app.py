from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from vilcos.routes import auth, websockets, users, roles
from vilcos.config import settings
from vilcos.utils import get_root_path
from vilcos.auth_utils import get_current_user
import os

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(get_root_path(), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])
app.include_router(users.router, tags=["users"])
app.include_router(roles.router, tags=["roles"])

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    max_age=settings.session_cookie_max_age,
    same_site=settings.session_cookie_samesite,
    https_only=settings.session_cookie_secure
)

@app.get("/")
async def home(request: Request):
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard(
    request: Request,
    user = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/signin", status_code=303)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )

# Basic database cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    from vilcos.db import engine
    await engine.dispose()
