from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from app.models.product import Product, ProductStatus
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """
    Product service class for product management (OOP)
    
    Encapsulates product-related business logic
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product
        
        Args:
            product_data: Product creation data
            
        Returns:
            Created product
            
        Raises:
            HTTPException: If SKU already exists or category not found
        """
        # Check if SKU already exists
        existing_product = self.db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )
        
        # Check if category exists
        if product_data.category_id is not None:
            category = self.db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {product_data.category_id} not found"
                )
        
        # Create product
        product = Product(**product_data.model_dump())
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return self.db.query(Product).filter(Product.sku == sku).first()
    
    def get_products(
        self, 
        page: int = 1, 
        page_size: int = 20, 
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """
        Get paginated list of products with filters
        
        Args:
            page: Page number
            page_size: Items per page
            status: Filter by status
            category_id: Filter by category
            search: Search in name or description
            
        Returns:
            Tuple of (products list, total count)
        """
        query = self.db.query(Product)
        
        # Apply filters
        if status:
            query = query.filter(Product.status == status)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        return products, total
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        """
        Update product
        
        Args:
            product_id: Product ID
            product_data: Update data
            
        Returns:
            Updated product
            
        Raises:
            HTTPException: If product not found or category not found
        """
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Check if category exists if it's being updated
        if "category_id" in update_data and update_data["category_id"] is not None:
            category = self.db.query(Category).filter(Category.id == update_data["category_id"]).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {update_data['category_id']} not found"
                )
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete product
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If product not found
        """
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        self.db.delete(product)
        self.db.commit()
        
        return True
    
    def check_stock_availability(self, product_id: int, quantity: int) -> bool:
        """
        Check if product has sufficient stock
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            
        Returns:
            True if stock is available
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        return product.is_in_stock(quantity)
    
    def reduce_stock(self, product_id: int, quantity: int) -> bool:
        """
        Reduce product stock (after successful payment)
        
        Args:
            product_id: Product ID
            quantity: Quantity to reduce
            
        Returns:
            True if successful
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        if product.reduce_stock(quantity):
            self.db.commit()
            return True
        
        return False