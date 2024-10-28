from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from vilcos.models import Table
from vilcos.database import get_db, manage_db
from vilcos.config import Settings
from vilcos.routes import auth, websockets

app = FastAPI(lifespan=manage_db)

# Load settings
settings = Settings()

# Initialize Redis
redis = aioredis.from_url(settings.redis_url)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="vilcos/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(websockets.router, prefix="/live", tags=["websockets"])

@app.get("/")
async def root():
    return {"message": "Welcome to Vilcos Framework"}

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

async def get_tables(session: AsyncSession) -> list:
    result = await session.execute(select(Table))
    return result.scalars().all()

@app.get("/booking")
async def booking_page(request: Request, session: AsyncSession = Depends(get_db)):
    tables = await get_tables(session)
    return templates.TemplateResponse("booking.html", {"request": request, "tables": tables})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
