from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from vilcos.database import get_db
from vilcos.models import Item, DiningTable, Reservation
from datetime import datetime
import stripe
from pydantic import BaseModel
from vilcos.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="vilcos/templates")

# Configure Stripe
stripe.api_key = settings.stripe_secret_key

# Pydantic models
class CreateCheckoutSessionRequest(BaseModel):
    amount: float
    order_type: str
    table_id: int | None = None

# Page routes
@router.get("/booking")
async def booking_page(request: Request):
    """Render the booking page"""
    return templates.TemplateResponse(
        "booking.html",
        {"request": request}
    )

@router.get("/menus")
async def menus_page(request: Request):
    """Render the menus page"""
    return templates.TemplateResponse(
        "menus.html",
        {"request": request}
    )

# API routes
@router.get("/api/menu-items")
async def get_menu_items(db: AsyncSession = Depends(get_db)):
    """Get all active menu items"""
    query = select(Item).where(Item.is_active == True)
    result = await db.execute(query)
    items = result.scalars().all()
    return {"menu_items": items}

@router.get("/api/tables")
async def get_tables(db: AsyncSession = Depends(get_db)):
    """Get all available tables"""
    query = select(DiningTable).where(DiningTable.is_active == True)
    result = await db.execute(query)
    tables = result.scalars().all()
    return {"tables": tables}

@router.post("/api/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest, req: Request):
    """Create a Stripe checkout session"""
    try:
        amount_cents = int(request.amount * 100)
        success_url = str(req.base_url) + "booking/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = str(req.base_url) + "booking/cancel"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': f'{"Dine-in" if request.table_id else "Pickup"} Order',
                    },
                },
                'quantity': 1,
            }],
            metadata={
                'order_type': request.order_type,
                'table_id': str(request.table_id) if request.table_id else None,
            },
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 

@router.get("/booking/success")
async def checkout_success(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Retrieve the checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status == "paid":
            # Extract metadata
            order_type = checkout_session.metadata.get('order_type')
            table_id = checkout_session.metadata.get('table_id')
            
            # Create reservation
            new_reservation = Reservation(
                table_id=int(table_id) if table_id else None,
                reservation_date=datetime.now(),
                status="confirmed",
                customer_name=checkout_session.customer_details.name,
                customer_email=checkout_session.customer_details.email,
                # You might want to add more fields based on your needs
            )
            
            db.add(new_reservation)
            await db.commit()
            
            return templates.TemplateResponse(
                "booking/success.html",
                {
                    "request": request,
                    "order_type": order_type,
                    "table_id": table_id,
                    "amount": checkout_session.amount_total / 100,  # Convert from cents
                    "customer_name": checkout_session.customer_details.name,
                    "customer_email": checkout_session.customer_details.email
                }
            )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/booking/cancel")
async def checkout_cancel(request: Request):
    return templates.TemplateResponse(
        "booking/cancel.html",
        {"request": request}
    )