from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from vilcos.db import manage_db, get_db, init_db
from vilcos.routes import auth, websockets
from vilcos.config import settings
from vilcos.utils import get_root_path
from vilcos.auth_utils import auth_required
from vilcos.schemas import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with manage_db(app):
        await init_db()
        yield

app = FastAPI(lifespan=lifespan)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(get_root_path(), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(get_root_path(), "templates"))

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

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
async def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
@auth_required(redirect_to_signin=True)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserSchema = None
):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })
