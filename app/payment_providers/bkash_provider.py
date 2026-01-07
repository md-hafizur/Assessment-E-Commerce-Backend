# app/payment_providers/bkash_provider.py

import uuid
from typing import Dict, Any
from app.payment_providers.base import PaymentProvider
from app.config import settings


class BkashProvider(PaymentProvider):
    """
    bKash payment provider with MOCK implementation
    
    For production: Replace with real bKash API integration
    For assessment: Demonstrates Strategy Pattern and payment flow
    """
    
    def __init__(self):
        self.provider_name = "bkash"
        # Mock mode - set to True for development/assessment
        self.mock_mode = settings.BKASH_MOCK_MODE if hasattr(settings, 'BKASH_MOCK_MODE') else True
    
    def create_payment(self, amount: float, order_id: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create bKash payment (MOCK for assessment)"""
        
        if self.mock_mode:
            # MOCK IMPLEMENTATION - For assessment/testing
            mock_payment_id = f"BKASH{uuid.uuid4().hex[:12].upper()}"
            
            return {
                "success": True,
                "transaction_id": mock_payment_id,
                "bkash_url": f"http://localhost:8000/mock-bkash-payment?paymentID={mock_payment_id}",
                "amount": str(amount),
                "status": "pending",
                "intent": "sale",
                "raw_response": {
                    "paymentID": mock_payment_id,
                    "bkashURL": f"http://localhost:8000/mock-bkash-payment?paymentID={mock_payment_id}",
                    "amount": str(amount),
                    "currency": "BDT",
                    "intent": "sale",
                    "merchantInvoiceNumber": f"INV_{order_id}",
                    "mode": "MOCK"
                }
            }
        
        # REAL IMPLEMENTATION - Would use actual bKash API
        else:
            try:
                token = self._get_token()
                # Real bKash API call here...
                pass
            except Exception as e:
                return {
                    "success": False,
                    "error": f"bKash API error: {str(e)}",
                    "transaction_id": None
                }
    
    def confirm_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Execute/confirm bKash payment"""
        
        if self.mock_mode:
            # MOCK: Simulate successful payment
            return {
                "success": True,
                "transaction_id": transaction_id,
                "trx_id": f"TRX{uuid.uuid4().hex[:10].upper()}",
                "status": "success",
                "amount": "0.00",
                "transactionStatus": "Completed",
                "raw_response": {
                    "paymentID": transaction_id,
                    "trxID": f"TRX{uuid.uuid4().hex[:10].upper()}",
                    "transactionStatus": "Completed",
                    "amount": "0.00",
                    "currency": "BDT"
                }
            }
        
        # Real implementation
        else:
            # Real bKash execute API call
            pass
    
    def query_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Query bKash payment status"""
        
        if self.mock_mode:
            # MOCK: Return completed status
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "success",
                "amount": "0.00",
                "transactionStatus": "Completed",
                "raw_response": {
                    "paymentID": transaction_id,
                    "transactionStatus": "Completed"
                }
            }
        
        # Real implementation
        else:
            # Real bKash query API call
            pass
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bKash callback/webhook"""
        
        if self.mock_mode:
            # MOCK: Process callback
            payment_id = payload.get("paymentID")
            status = payload.get("status", "success")
            
            return {
                "success": True,
                "transaction_id": payment_id,
                "status": "success" if status == "success" else "failed",
                "raw_response": payload
            }
        
        # Real implementation
        else:
            # Real bKash webhook processing
            pass
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name
    
    def _get_token(self) -> str:
        """Get bKash auth token (only for real mode)"""
        if self.mock_mode:
            return "mock_token"
        
        # Real token generation
        import requests
        url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant"
        # ... real implementation
        pass