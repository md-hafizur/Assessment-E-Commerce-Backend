from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new category (Admin only)
    """
    category_service = CategoryService(db)
    category = category_service.create_category(category_data)
    return category


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(
    db: Session = Depends(get_db)
):
    """
    Get all categories
    """
    category_service = CategoryService(db)
    categories = category_service.get_all_categories()
    return categories


@router.get("/tree", response_model=List[CategoryTreeResponse])
def get_category_tree(
    db: Session = Depends(get_db)
):
    """
    Get category tree (nested structure)
    """
    category_service = CategoryService(db)
    category_tree = category_service.build_category_tree()
    return category_tree


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get category by ID
    """
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a category (Admin only)
    """
    category_service = CategoryService(db)
    category = category_service.update_category(category_id, category_data)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a category (Admin only)
    """
    category_service = CategoryService(db)
    category_service.delete_category(category_id)
    return None


@router.post("/cache/invalidate", status_code=status.HTTP_204_NO_CONTENT)
def invalidate_category_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Invalidate category tree cache (Admin only)
    """
    category_service = CategoryService(db)
    category_service.invalidate_category_tree_cache()
    return None