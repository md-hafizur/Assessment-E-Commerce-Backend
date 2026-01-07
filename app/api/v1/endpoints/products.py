from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.models.user import User
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.product_service import ProductService
from app.config import settings

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new product (Admin only)
    
    - **name**: Product name
    - **sku**: Unique SKU
    - **description**: Product description
    - **price**: Product price
    - **stock**: Available stock
    - **status**: active or inactive
    - **category_id**: Optional category ID
    """
    product_service = ProductService(db)
    product = product_service.create_product(product_data)
    return product


@router.get("/", response_model=ProductListResponse)
def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = Query(None, regex="^(active|inactive)$"),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of products with filters
    
    - **page**: Page number
    - **page_size**: Items per page
    - **status**: Filter by status (active/inactive)
    - **category_id**: Filter by category
    - **search**: Search in name or description
    """
    product_service = ProductService(db)
    products, total = product_service.get_products(page, page_size, status, category_id, search)
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product_service = ProductService(db)
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update product (Admin only)"""
    product_service = ProductService(db)
    product = product_service.update_product(product_id, product_data)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete product (Admin only)"""
    product_service = ProductService(db)
    product_service.delete_product(product_id)
    return None