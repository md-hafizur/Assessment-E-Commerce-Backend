from typing import Dict
from app.payment_providers.base import PaymentProvider
from app.payment_providers.stripe_provider import StripeProvider
from app.payment_providers.bkash_provider import BkashProvider


class PaymentFactory:
    """
    Factory class for creating payment providers (Strategy Pattern)
    
    This centralizes provider instantiation and makes it easy to add
    new payment providers without modifying existing code.
    """
    
    _providers: Dict[str, PaymentProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider: PaymentProvider):
        """Register a new payment provider"""
        cls._providers[name] = provider
    
    @classmethod
    def get_provider(cls, provider_name: str) -> PaymentProvider:
        """
        Get payment provider by name
        
        Args:
            provider_name: Provider name (stripe, bkash, etc.)
            
        Returns:
            PaymentProvider instance
            
        Raises:
            ValueError: If provider not found
        """
        if provider_name not in cls._providers:
            raise ValueError(f"Payment provider '{provider_name}' not found")
        
        return cls._providers[provider_name]
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())


# Register available providers
PaymentFactory.register_provider("stripe", StripeProvider())
PaymentFactory.register_provider("bkash", BkashProvider())


__all__ = ["PaymentFactory", "PaymentProvider", "StripeProvider", "BkashProvider"]