from sqlalchemy import Column, Integer, Numeric, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"


class Order(Base):
    """Order model representing customer orders"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
    
    def calculate_total(self) -> float:
        """Calculate total amount from order items"""
        total = sum(item.subtotal for item in self.order_items)
        self.total_amount = total
        return float(total)
    
    def mark_as_paid(self):
        """Mark order as paid and reduce stock"""
        self.status = OrderStatus.PAID
        for item in self.order_items:
            item.product.reduce_stock(item.quantity)
    
    def cancel(self):
        """Cancel the order"""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELED
            return True
        return False