from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import redis.asyncio as aioredis
from vilcos.database import manage_db
from vilcos.routes.api import router as api_router
from vilcos.routes import auth, websockets
from vilcos.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Initialize Redis
redis = aioredis.from_url(settings.redis_url)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount static files
app.mount("/static", StaticFiles(directory="vilcos/static"), name="static")

# Templates
templates = Jinja2Templates(directory="vilcos/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(websockets.router, prefix="/live", tags=["websockets"])
app.include_router(api_router)

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.on_event("startup")
async def startup():
    async with manage_db(app):
        pass
