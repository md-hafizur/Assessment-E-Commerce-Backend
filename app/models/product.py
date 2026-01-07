from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ProductStatus(str, enum.Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Product(Base):
    """Product model with inventory management"""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"
    
    def reduce_stock(self, quantity: int) -> bool:
        """Reduce product stock safely"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def is_in_stock(self, quantity: int = 1) -> bool:
        """Check if product has sufficient stock"""
        return self.stock >= quantity and self.status == ProductStatus.ACTIVE