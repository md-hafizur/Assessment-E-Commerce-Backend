from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    product_id: int
    quantity: int
    price: Decimal
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for paginated order list"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int