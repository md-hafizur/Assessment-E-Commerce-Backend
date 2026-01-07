from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = None  # Added slug field
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(CategoryBase):
    """Schema for updating a category"""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CategoryTreeResponse(CategoryResponse):
    """Schema for nested category tree response"""
    children: List["CategoryTreeResponse"] = []

# Update forward refs
CategoryTreeResponse.model_rebuild()