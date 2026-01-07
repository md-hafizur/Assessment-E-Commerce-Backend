from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class PaymentCreate(BaseModel):
    """Schema for initiating a payment"""
    order_id: int = Field(..., gt=0)
    provider: str = Field(..., pattern="^(stripe|bkash)$")


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    id: int
    order_id: int
    provider: str
    transaction_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StripePaymentIntentResponse(BaseModel):
    """Schema for Stripe payment intent response"""
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str = "usd"


class BkashPaymentResponse(BaseModel):
    """Schema for bKash payment response"""
    payment_id: str
    bkash_url: str
    amount: str
    intent: str


class PaymentConfirmation(BaseModel):
    """Schema for payment confirmation"""
    payment_id: int
    provider: str
    transaction_id: str


class WebhookStripe(BaseModel):
    """Schema for Stripe webhook"""
    event_type: str
    payment_intent_id: str
    status: str
    metadata: Optional[Dict[str, Any]] = None


class WebhookBkash(BaseModel):
    """Schema for bKash webhook/callback"""
    payment_id: str
    status: str
    trx_id: Optional[str] = None