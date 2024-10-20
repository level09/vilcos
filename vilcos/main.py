# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from vilcos.config import Settings
from vilcos.routes import auth
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

@app.get("/")
async def root():
    return {"message": "Welcome to Vilcos Framework"}

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

async def get_session_data(session_id: str):
    session_data = await redis.get(session_id)
    return session_data if session_data else {}

@app.get("/set-session")
async def set_session(request: Request):
    session_id = str(uuid.uuid4())
    await redis.set(session_id, {'your_email': 'yourmail@somedomain.com'})
    response = {"message": "Session data set"}
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.get("/get-session")
async def get_session(request: Request):
    session_id = request.cookies.get("session_id")
    session_data = await get_session_data(session_id)
    return {"your_email": session_data.get('your_email')}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
