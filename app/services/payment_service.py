from sqlalchemy.orm import Session
from typing import Dict, Any
from fastapi import HTTPException, status
from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.models.order import Order, OrderStatus
from app.payment_providers import PaymentFactory
from app.services.order_service import OrderService


class PaymentService:
    """
    Payment service class for payment management (OOP)
    
    Uses Strategy Pattern to support multiple payment providers
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.order_service = OrderService(db)
    
    def create_payment(
        self, 
        order_id: int, 
        provider_name: str, 
        user_id: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create payment using Strategy Pattern
        
        Args:
            order_id: Order ID
            provider_name: Payment provider (stripe/bkash)
            user_id: User ID for authorization
            metadata: Additional metadata
            
        Returns:
            Payment creation response
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate order
        order = self.order_service.get_order_by_id(order_id, user_id)
        
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in pending status"
            )
        
        # Get payment provider using Strategy Pattern
        try:
            provider = PaymentFactory.get_provider(provider_name)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Create payment with provider
        amount = float(order.total_amount)
        result = provider.create_payment(amount, order_id, metadata)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment creation failed")
            )
        
        # Save payment to database
        payment = Payment(
            order_id=order_id,
            provider=provider_name,
            transaction_id=result["transaction_id"],
            status=PaymentStatus.PENDING,
            raw_response=result.get("raw_response")
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "provider": provider_name,
            "transaction_id": result["transaction_id"],
            **result
        }
    
    def confirm_payment(self, payment_id: int, transaction_id: str) -> Payment:
        """
        Confirm/execute payment
        
        Args:
            payment_id: Payment ID
            transaction_id: Transaction ID from provider
            
        Returns:
            Updated payment
            
        Raises:
            HTTPException: If confirmation fails
        """
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Get provider using Strategy Pattern
        provider = PaymentFactory.get_provider(payment.provider)
        
        # Confirm payment with provider
        result = provider.confirm_payment(transaction_id)
        
        if not result.get("success"):
            payment.mark_as_failed()
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment confirmation failed")
            )
        
        stripe_status = result.get("status")
        
        # Update payment status based on Stripe's status
        # Consider 'succeeded' as success, 'requires_payment_method', 'requires_action' as still pending client-side action
        if stripe_status == "succeeded":
            payment.mark_as_success()
            payment.raw_response = result.get("raw_response")
            self.order_service.mark_order_as_paid(payment.order_id)
        elif stripe_status in ["requires_payment_method", "requires_action", "processing"]:
            # Payment is still in progress, do not mark as failed or success yet
            # Keep as PENDING in our system or update to a more granular status if available
            # For now, we keep it as PENDING and rely on webhooks for final status
            pass # Keep payment status as PENDING
        else:
            payment.mark_as_failed()
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def query_payment(self, payment_id: int) -> Payment: # Changed return type to Payment
        """
        Query payment status
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status
        """
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Get provider using Strategy Pattern
        provider = PaymentFactory.get_provider(payment.provider)
        
        # Query payment status
        provider_result = provider.query_payment(payment.transaction_id)
        
        # Update payment status if provider_result indicates a change
        if provider_result.get("status") == "succeeded" and payment.status != PaymentStatus.SUCCESS:
            payment.mark_as_success()
            payment.raw_response = provider_result.get("raw_response")
            self.db.commit()
            self.db.refresh(payment)
        elif provider_result.get("status") == "failed" and payment.status != PaymentStatus.FAILED:
            payment.mark_as_failed()
            payment.raw_response = provider_result.get("raw_response")
            self.db.commit()
            self.db.refresh(payment)

        # Return the Payment object directly, as it matches PaymentResponse schema structure
        return payment
    
    def handle_webhook(self, provider_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook from payment provider
        
        Args:
            provider_name: Payment provider
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        # Get provider using Strategy Pattern
        try:
            provider = PaymentFactory.get_provider(provider_name)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Process webhook
        result = provider.handle_webhook(payload)
        
        if not result.get("success"):
            return result
        
        # Update payment in database
        transaction_id = result.get("transaction_id")
        if transaction_id:
            payment = self.db.query(Payment).filter(
                Payment.transaction_id == transaction_id
            ).first()
            
            if payment:
                if result.get("status") == "success":
                    payment.mark_as_success()
                    payment.raw_response = result.get("raw_response")
                    
                    # Mark order as paid
                    self.order_service.mark_order_as_paid(payment.order_id)
                    
                elif result.get("status") == "failed":
                    payment.mark_as_failed()
                    payment.raw_response = result.get("raw_response")
                
                self.db.commit()
        
        return result
    
    def get_payment_by_order(self, order_id: int) -> Payment:
        """Get payment by order ID"""
        payment = self.db.query(Payment).filter(Payment.order_id == order_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found for this order"
            )
        
        return payment