from sqlalchemy.orm import Session
from typing import List, Tuple
from fastapi import HTTPException, status
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderItemCreate


class OrderService:
    """
    Order service class for order management (OOP)
    
    Encapsulates order-related business logic including
    total calculation algorithm
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """
        Create a new order with items
        
        Args:
            user_id: User ID
            order_data: Order creation data
            
        Returns:
            Created order
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate all products and check stock
        order_items_data = []
        
        for item_data in order_data.items:
            product = self.db.query(Product).filter(
                Product.id == item_data.product_id
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item_data.product_id} not found"
                )
            
            if not product.is_in_stock(item_data.quantity):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product: {product.name}"
                )
            
            order_items_data.append({
                "product": product,
                "quantity": item_data.quantity,
                "price": product.price
            })
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=0,
            status=OrderStatus.PENDING
        )
        
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Create order items and calculate total (Algorithm requirement)
        total_amount = 0
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["price"],
                subtotal=0
            )
            
            # Calculate subtotal (deterministic algorithm)
            order_item.calculate_subtotal()
            total_amount += order_item.subtotal
            
            self.db.add(order_item)
        
        # Set total amount (deterministic algorithm)
        order.total_amount = total_amount
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def get_order_by_id(self, order_id: int, user_id: int = None) -> Order:
        """
        Get order by ID
        
        Args:
            order_id: Order ID
            user_id: Optional user ID for authorization
            
        Returns:
            Order
            
        Raises:
            HTTPException: If not found or unauthorized
        """
        query = self.db.query(Order).filter(Order.id == order_id)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        order = query.first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
    
    def get_user_orders(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[Order], int]:
        """
        Get paginated list of user orders
        
        Args:
            user_id: User ID
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (orders list, total count)
        """
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(page_size).all()
        
        return orders, total
    
    def cancel_order(self, order_id: int, user_id: int) -> Order:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            user_id: User ID
            
        Returns:
            Canceled order
            
        Raises:
            HTTPException: If cannot cancel
        """
        order = self.get_order_by_id(order_id, user_id)
        
        if not order.cancel():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel order. Order must be in pending status."
            )
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def mark_order_as_paid(self, order_id: int) -> Order:
        """
        Mark order as paid and reduce stock (Algorithm requirement)
        
        This implements the stock reduction algorithm after successful payment
        
        Args:
            order_id: Order ID
            
        Returns:
            Updated order
        """
        order = self.get_order_by_id(order_id)
        
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in pending status"
            )
        
        # Mark as paid and reduce stock (deterministic algorithm)
        order.mark_as_paid()
        
        self.db.commit()
        self.db.refresh(order)
        
        return order