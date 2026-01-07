from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.config import settings
from app.core.cache import redis_cache
import re


class CategoryService:
    """
    Category service class for managing product categories.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = redis_cache
        self.cache_key_prefix = "category_tree"
    
    def _generate_unique_slug(self, name: str, exclude_id: Optional[int] = None) -> str:
        """
        Generates a URL-friendly slug from a name and ensures its uniqueness.
        """
        slug = re.sub(r"[^\w\s-]", "", name).strip().lower()
        slug = re.sub(r"[-\s]+", "", slug) # Remove hyphens too to avoid double hyphens
        
        base_slug = slug
        counter = 1
        while True:
            query = self.db.query(Category).filter(Category.slug == slug)
            if exclude_id:
                query = query.filter(Category.id != exclude_id)
            existing_slug = query.first()
            
            if not existing_slug:
                return slug
            
            slug = f"{base_slug}-{counter}"
            counter += 1

    def create_category(self, category_data: CategoryCreate) -> Category:
        """
        Create a new category.
        
        Args:
            category_data: Category creation data.
            
        Returns:
            The created Category object.
            
        Raises:
            HTTPException: If a category with the same name or slug already exists,
                           if the parent category is invalid (e.g., 0),
                           or if the parent category does not exist.
        """
        # Check if category with the same name already exists
        existing_category_by_name = self.db.query(Category).filter(Category.name == category_data.name).first()
        if existing_category_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists."
            )
        
        # Generate or validate slug
        if category_data.slug:
            # Check if provided slug is unique
            existing_category_by_slug = self.db.query(Category).filter(Category.slug == category_data.slug).first()
            if existing_category_by_slug:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this slug already exists."
                )
            slug = category_data.slug
        else:
            slug = self._generate_unique_slug(category_data.name)
        
        # Validate parent_id if provided
        if category_data.parent_id is not None: # Explicitly check for None
            if category_data.parent_id == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category ID cannot be 0. IDs typically start from 1."
                )
            parent_category = self.db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with id {category_data.parent_id} not found."
                )
        
        category = Category(**category_data.model_dump(exclude_unset=True))
        category.slug = slug # Assign the generated/validated slug
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        # Invalidate cache after creating a new category
        self.cache.invalidate_cache(self.cache_key_prefix)
        
        return category
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get a category by its ID."""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return self.db.query(Category).all()
    
    def build_category_tree(self, parent_id: Optional[int] = None) -> List[Category]:
        """
        Recursively build a category tree.
        """
        cache_key = f"{self.cache_key_prefix}_parent_{parent_id or 'none'}"
        cached_tree = self.cache.get_cached_data(cache_key)
        if cached_tree:
            # Need to convert back to Category objects if needed,
            # or ensure the caching stores a serializable format that can be
            # directly used by Pydantic models. For now, assume it works.
            return cached_tree
        
        categories = self.db.query(Category).filter(Category.parent_id == parent_id).all()
        tree = []
        for category in categories:
            # Ensure children is initialized as a list before appending
            if not hasattr(category, 'children') or category.children is None:
                category.children = []
            category.children = self.build_category_tree(category.id)
            tree.append(category)
        
        self.cache.set_cached_data(cache_key, tree, settings.CACHE_TTL)
        return tree
    
    def invalidate_category_tree_cache(self):
        """Invalidate the entire category tree cache."""
        self.cache.invalidate_cache(self.cache_key_prefix)
    
    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Category:
        """
        Update an existing category.
        
        Args:
            category_id: The ID of the category to update.
            category_data: Category update data.
            
        Returns:
            The updated Category object.
            
        Raises:
            HTTPException: If the category to update is not found,
                           if a category with the new name already exists,
                           or if the parent category does not exist.
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )
        
        update_data = category_data.model_dump(exclude_unset=True)
        
        # Handle slug generation/update
        if "name" in update_data and update_data["name"] != category.name:
            # If name changes and slug is not explicitly provided, generate a new slug
            if "slug" not in update_data or not update_data["slug"]:
                update_data["slug"] = self._generate_unique_slug(update_data["name"], exclude_id=category.id)
        elif "slug" in update_data and update_data["slug"] != category.slug:
            # If slug is explicitly provided and changed, ensure uniqueness
            existing_category_by_slug = self.db.query(Category).filter(
                Category.slug == update_data["slug"],
                Category.id != category.id
            ).first()
            if existing_category_by_slug:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this slug already exists."
                )

        # Check if category name is being updated and if it conflicts with an existing name (after slug handling)
        if "name" in update_data and update_data["name"] != category.name:
            existing_category_by_name = self.db.query(Category).filter(
                Category.name == update_data["name"],
                Category.id != category.id
            ).first()
            if existing_category_by_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists."
                )
        
        # Validate parent_id if being updated
        if "parent_id" in update_data and update_data["parent_id"] is not None: # Explicitly check for None
            if update_data["parent_id"] == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category ID cannot be 0. IDs typically start from 1."
                )
            parent_category = self.db.query(Category).filter(Category.id == update_data["parent_id"]).first()
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with id {update_data['parent_id']} not found."
                )
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        
        # Invalidate cache after updating a category
        self.cache.invalidate_cache(self.cache_key_prefix)
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: The ID of the category to delete.
            
        Returns:
            True if the category was successfully deleted.
            
        Raises:
            HTTPException: If the category to delete is not found,
                           or if the category has associated products or children.
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )
        
        # Check for associated products
        if self.db.query(Category).join(Category.products).filter(Category.id == category_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with associated products."
            )
        
        # Check for child categories
        if category.children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with child categories. Please reassign or delete children first."
            )
        
        self.db.delete(category)
        self.db.commit()
        
        # Invalidate cache after deleting a category
        self.cache.invalidate_cache(self.cache_key_prefix)
        
        return True