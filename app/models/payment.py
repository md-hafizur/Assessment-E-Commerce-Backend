from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class PaymentProvider(str, enum.Enum):
    """Payment provider enumeration"""
    STRIPE = "stripe"
    BKASH = "bkash"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Payment(Base):
    """Payment model for tracking payment transactions"""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(Enum(PaymentProvider), nullable=False, index=True)
    transaction_id = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    raw_response = Column(JSON, nullable=True)  # Store complete provider response
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, provider='{self.provider}', status='{self.status}')>"
    
    def mark_as_success(self):
        """Mark payment as successful"""
        self.status = PaymentStatus.SUCCESS
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED