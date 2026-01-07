from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.order_service import OrderService
from app.config import settings

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order
    
    - **items**: List of order items with product_id and quantity
    
    The system will:
    1. Validate all products exist and have sufficient stock
    2. Calculate subtotals and total amount (deterministic algorithm)
    3. Create order with PENDING status
    """
    order_service = OrderService(db)
    order = order_service.create_order(current_user.id, order_data)
    return order


@router.get("/", response_model=OrderListResponse)
def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of current user's orders
    
    - **page**: Page number
    - **page_size**: Items per page
    """
    order_service = OrderService(db)
    orders, total = order_service.get_user_orders(current_user.id, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": orders,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order by ID (only for order owner)"""
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id, current_user.id)
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order
    
    Can only cancel orders in PENDING status.
    """
    order_service = OrderService(db)
    order = order_service.cancel_order(order_id, current_user.id)
    return order