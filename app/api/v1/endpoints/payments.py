from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentConfirmation
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create payment using Strategy Pattern
    
    - **order_id**: Order ID to pay for
    - **provider**: Payment provider (stripe or bkash)
    
    Flow:
    1. Validates order belongs to user and is in PENDING status
    2. Creates payment intent with selected provider (Strategy Pattern)
    3. Returns payment details for frontend to complete
    
    For Stripe: Returns client_secret for Stripe Elements
    For bKash: Returns bkash_url to redirect user
    """
    payment_service = PaymentService(db)
    
    # Create payment with selected provider
    result = payment_service.create_payment(
        order_id=payment_data.order_id,
        provider_name=payment_data.provider,
        user_id=current_user.id,
        metadata={"user_email": current_user.email}
    )
    
    return result


@router.post("/confirm")
def confirm_payment(
    confirmation: PaymentConfirmation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm/execute payment
    
    - **payment_id**: Payment ID from create_payment
    - **provider**: Payment provider
    - **transaction_id**: Transaction ID from provider
    
    This endpoint:
    1. Confirms payment with provider
    2. Updates payment status
    3. Marks order as PAID
    4. Reduces product stock (deterministic algorithm)
    """
    payment_service = PaymentService(db)
    payment = payment_service.confirm_payment(
        payment_id=confirmation.payment_id,
        transaction_id=confirmation.transaction_id
    )
    
    return {
        "message": "Payment confirmed successfully",
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "status": payment.status
    }


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment details"""
    payment_service = PaymentService(db)
    result = payment_service.query_payment(payment_id)
    return result


@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment by order ID"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_order(order_id)
    return payment


# Webhook endpoints
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe webhook handler
    
    Receives payment status updates from Stripe.
    Automatically updates payment and order status.
    """
    payload = await request.json()
    
    payment_service = PaymentService(db)
    result = payment_service.handle_webhook("stripe", payload)
    
    return {"status": "received", "result": result}


@router.post("/webhooks/bkash")
async def bkash_webhook(request: Request, db: Session = Depends(get_db)):
    """
    bKash callback handler
    
    Receives payment status from bKash after user completes payment.
    Updates payment and order status accordingly.
    """
    payload = await request.json()
    
    payment_service = PaymentService(db)
    result = payment_service.handle_webhook("bkash", payload)
    
    return {"status": "received", "result": result}


@router.get("/providers")
def get_available_providers():
    """Get list of available payment providers"""
    from app.payment_providers import PaymentFactory
    
    providers = PaymentFactory.get_available_providers()
    return {
        "providers": providers,
        "count": len(providers)
    }