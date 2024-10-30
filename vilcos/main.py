from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime

from vilcos.models import DiningTable, Reservation, Item
from vilcos.database import get_db, manage_db
from vilcos.config import Settings
from vilcos.routes import auth, websockets

app = FastAPI()

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

# Define a Pydantic model for the reservation request
class ReservationRequest(BaseModel):
    table_id: int
    time_slot_id: int
    reservation_date: datetime
    party_size: int
    customer_name: str
    customer_email: str
    customer_phone: str
    special_requests: str = None

@app.get("/")
async def root():
    # redirect to booking page
    return RedirectResponse(url="/booking")
    

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/menus")
async def menus_page(request: Request):
    return templates.TemplateResponse("menus.html", {"request": request})

@app.get("/booking")
async def booking_page(request: Request):
    return templates.TemplateResponse("booking.html", {"request": request})

@app.get("/api/tables")
async def list_tables(db: AsyncSession = Depends(get_db)):
    # Fetch all tables
    result = await db.execute(select(DiningTable))
    tables = result.scalars().all()

    # Prepare the response with reservation status
    tables_with_status = []
    for table in tables:
        # Check if the table has any active reservations
        reservation_query = select(Reservation).where(
            Reservation.table_id == table.id,
            Reservation.status == "confirmed"
        )
        reservation = (await db.execute(reservation_query)).scalars().first()
        
        # Add reservation status to the table data
        table_data = table.__dict__.copy()
        table_data['is_reserved'] = reservation is not None
        tables_with_status.append(table_data)

    return {"tables": tables_with_status}

@app.post("/api/reserve")
async def reserve_table(request: ReservationRequest, db: AsyncSession = Depends(get_db)):
    # Check for existing reservation
    query = select(Reservation).where(
        Reservation.table_id == request.table_id,
        Reservation.time_slot_id == request.time_slot_id,
        Reservation.reservation_date == request.reservation_date
    )
    if (await db.execute(query)).scalars().first():
        raise HTTPException(status_code=400, detail="Table already reserved.")

    # Create and save new reservation
    reservation = Reservation(**request.model_dump(), status="confirmed")
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    return {"message": "Reservation confirmed", "reservation_id": reservation.id}

@app.get("/api/menu-items")
async def list_menu_items(db: AsyncSession = Depends(get_db)):
    # Fetch all menu items
    result = await db.execute(select(Item))
    items = result.scalars().all()

    # Prepare the response
    menu_items = []
    for item in items:
        item_data = item.__dict__.copy()
        menu_items.append(item_data)

    return {"menu_items": menu_items}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
