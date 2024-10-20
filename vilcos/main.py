# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from vilcos.config import Settings
from vilcos.routes import auth, websockets  # Import the new WebSocket routes
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
import redis.asyncio as aioredis
import uuid

app = FastAPI()

# Load settings
settings = Settings()

# Initialize Redis
redis = aioredis.from_url(settings.redis_url)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="vilcos/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include WebSocket routers
app.include_router(websockets.router, prefix="/live", tags=["websockets"])

@app.get("/")
async def root():
    return {"message": "Welcome to Vilcos Framework"}

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
