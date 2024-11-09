from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import stripe
from vilcos.config import settings

router = APIRouter()

# Configure Stripe
stripe.api_key = settings.stripe_secret_key

class CreateCheckoutSessionRequest(BaseModel):
    amount: float
    order_type: str
    table_id: int | None = None

@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest, req: Request):
    try:
        # Convert amount to cents
        amount_cents = int(request.amount * 100)
        
        success_url = str(req.base_url) + "booking/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = str(req.base_url) + "booking/cancel"

        # Create Checkout Session
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