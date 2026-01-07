from abc import ABC, abstractmethod
from typing import Dict, Any


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers (Strategy Pattern)
    
    This allows easy addition of new payment providers without modifying
    existing code - just implement this interface.
    """
    
    @abstractmethod
    def create_payment(self, amount: float, order_id: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a payment intent/session
        
        Args:
            amount: Payment amount
            order_id: Associated order ID
            metadata: Additional payment metadata
            
        Returns:
            Dictionary containing payment details
        """
        pass
    
    @abstractmethod
    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Confirm/execute a payment
        
        Args:
            transaction_id: Payment transaction ID
            
        Returns:
            Dictionary containing confirmation status
        """
        pass
    
    @abstractmethod
    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Query payment status
        
        Args:
            transaction_id: Payment transaction ID
            
        Returns:
            Dictionary containing payment status
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook/callback from payment provider
        
        Args:
            payload: Webhook payload
            
        Returns:
            Dictionary containing processed webhook data
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get payment provider name
        
        Returns:
            Provider name (stripe, bkash, etc.)
        """
        pass