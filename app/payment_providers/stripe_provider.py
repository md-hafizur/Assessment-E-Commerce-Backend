import stripe
import logging
from typing import Dict, Any
from app.payment_providers.base import PaymentProvider
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class StripeProvider(PaymentProvider):
    """Stripe payment provider implementation"""
    
    def __init__(self):
        self.provider_name = "stripe"
    
    def create_payment(self, amount: float, order_id: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create Stripe PaymentIntent
        """
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata={
                    "order_id": order_id,
                    **(metadata or {})
                },
                automatic_payment_methods={"enabled": True}
            )
            
            logger.info(f"Stripe PaymentIntent created: {payment_intent.id}, Status: {payment_intent.status}")
            
            return {
                "success": True,
                "transaction_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status,
                "amount": amount_cents,
                "currency": "usd",
                "raw_response": payment_intent
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe PaymentIntent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": None
            }
    
    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Confirm Stripe payment (by retrieving its latest status)
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            logger.info(f"Stripe PaymentIntent retrieved for confirmation: {payment_intent.id}, Status: {payment_intent.status}")
            
            # Here, we only retrieve the status. Actual confirmation happens client-side.
            # The status will be 'succeeded' if confirmed, 'requires_action', etc.
            return {
                "success": True,
                "transaction_id": payment_intent.id,
                "status": payment_intent.status, # Return actual status from Stripe
                "amount": payment_intent.amount,
                "raw_response": payment_intent
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve Stripe PaymentIntent for confirmation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Query Stripe payment status
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            logger.info(f"Stripe PaymentIntent queried: {payment_intent.id}, Status: {payment_intent.status}")
            
            return {
                "success": True,
                "transaction_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "raw_response": payment_intent
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to query Stripe PaymentIntent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook
        """
        try:
            event_type = payload.get("type")
            data = payload.get("data", {}).get("object", {})
            
            logger.info(f"Stripe Webhook received: Event Type={event_type}, PaymentIntent ID={data.get('id')}")
            
            if event_type == "payment_intent.succeeded":
                return {
                    "success": True,
                    "event_type": event_type,
                    "transaction_id": data.get("id"),
                    "status": "success",
                    "order_id": data.get("metadata", {}).get("order_id"),
                    "raw_response": payload
                }
            
            elif event_type == "payment_intent.payment_failed":
                return {
                    "success": True,
                    "event_type": event_type,
                    "transaction_id": data.get("id"),
                    "status": "failed",
                    "order_id": data.get("metadata", {}).get("order_id"),
                    "raw_response": payload
                }
            
            return {
                "success": True,
                "event_type": event_type,
                "message": "Event received but not processed"
            }
        
        except Exception as e:
            logger.error(f"Failed to handle Stripe webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name