"""
Purchase order service for procurement operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus, PurchaseOrderItem
from models.supplier import Supplier
from models.item import Item
from schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderItemCreate, PurchaseOrderItemResponse
)
from utils.notifications import send_purchase_order_notification
from utils.validation import validate_purchase_order
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    """Service for handling purchase order operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_purchase_order(
        self, 
        order_data: PurchaseOrderCreate, 
        created_by: uuid.UUID
    ) -> PurchaseOrderResponse:
        """Create a new purchase order
        
        Args:
            order_data: Purchase order creation data
            created_by: User ID who created the order
            
        Returns:
            Created purchase order
            
        Raises:
            HTTPException: If validation fails or supplier not found
        """
        # Validate supplier exists
        supplier = self.session.get(Supplier, order_data.supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        if not supplier.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create order for inactive supplier"
            )
        
        # Validate purchase order data
        validation_errors = validate_purchase_order(order_data.model_dump())
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": validation_errors}
            )
        
        # Generate order number
        order_number = await self._generate_order_number()
        
        # Calculate expected delivery date
        expected_delivery_date = date.today() + timedelta(days=supplier.average_delivery_time)
        
        # Create purchase order
        purchase_order = PurchaseOrder(
            order_number=order_number,
            supplier_id=order_data.supplier_id,
            status=PurchaseOrderStatus.PENDING,
            order_date=date.today(),
            expected_delivery_date=expected_delivery_date,
            notes=order_data.notes,
            created_by=created_by
        )
        
        self.session.add(purchase_order)
        self.session.flush()  # Get the ID
        
        # Add order items and calculate total
        total_cost = Decimal('0.00')
        
        for item_data in order_data.items:
            # Validate item exists
            item = self.session.get(Item, item_data.item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item {item_data.item_id} not found"
                )
            
            # Create order item
            order_item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price or item.unit_cost,
                total_price=item_data.quantity * (item_data.unit_price or item.unit_cost)
            )
            
            self.session.add(order_item)
            total_cost += order_item.total_price
        
        purchase_order.total_cost = total_cost
        
        self.session.commit()
        self.session.refresh(purchase_order)
        
        # Send notification to supplier (mock)
        try:
            await send_purchase_order_notification(
                supplier_id=str(supplier.id),
                order_data={
                    "order_number": order_number,
                    "supplier_name": supplier.name,
                    "total_cost": float(total_cost),
                    "expected_delivery": expected_delivery_date.isoformat(),
                    "items_count": len(order_data.items)
                },
                notification_type="order_created"
            )
        except Exception as e:
            logger.error(f"Failed to send purchase order notification: {str(e)}")
        
        logger.info(f"Created purchase order {order_number} for supplier {supplier.name}")
        return await self._to_response(purchase_order)
    
    async def get_purchase_order(self, order_id: uuid.UUID) -> PurchaseOrderResponse:
        """Get purchase order by ID
        
        Args:
            order_id: Purchase order UUID
            
        Returns:
            Purchase order details
            
        Raises:
            HTTPException: If order not found
        """
        order = self.session.get(PurchaseOrder, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        return await self._to_response(order)
    
    async def get_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        supplier_id: Optional[uuid.UUID] = None,
        status: Optional[PurchaseOrderStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        overdue_only: bool = False
    ) -> List[PurchaseOrderResponse]:
        """Get purchase orders with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            supplier_id: Filter by supplier ID
            status: Filter by order status
            start_date: Filter orders from this date
            end_date: Filter orders until this date
            overdue_only: Show only overdue orders
            
        Returns:
            List of purchase orders
        """
        query = select(PurchaseOrder)
        
        # Apply filters
        conditions = []
        
        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)
        
        if status:
            conditions.append(PurchaseOrder.status == status)
        
        if start_date:
            conditions.append(PurchaseOrder.order_date >= start_date)
        
        if end_date:
            conditions.append(PurchaseOrder.order_date <= end_date)
        
        if overdue_only:
            conditions.extend([
                PurchaseOrder.expected_delivery_date < date.today(),
                PurchaseOrder.status.in_([PurchaseOrderStatus.PENDING, PurchaseOrderStatus.APPROVED])
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit)
        orders = self.session.exec(query).all()
        
        return [await self._to_response(order) for order in orders]
    
    async def update_purchase_order(
        self, 
        order_id: uuid.UUID, 
        order_data: PurchaseOrderUpdate
    ) -> PurchaseOrderResponse:
        """Update purchase order information
        
        Args:
            order_id: Purchase order UUID
            order_data: Update data
            
        Returns:
            Updated purchase order
            
        Raises:
            HTTPException: If order not found or cannot be updated
        """
        order = self.session.get(PurchaseOrder, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        # Check if order can be updated
        if order.status in [PurchaseOrderStatus.DELIVERED, PurchaseOrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update order with status {order.status}"
            )
        
        # Update fields
        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'items':  # Handle items separately
                setattr(order, field, value)
        
        order.updated_at = datetime.utcnow()
        
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        
        logger.info(f"Updated purchase order {order_id}")
        return await self._to_response(order)
    
    async def approve_purchase_order(self, order_id: uuid.UUID, approved_by: uuid.UUID) -> dict:
        """Approve a purchase order
        
        Args:
            order_id: Purchase order UUID
            approved_by: User ID who approved the order
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If order not found or cannot be approved
        """
        order = self.session.get(PurchaseOrder, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        if order.status != PurchaseOrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve order with status {order.status}"
            )
        
        order.status = PurchaseOrderStatus.APPROVED
        order.approved_by = approved_by
        order.approved_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        
        self.session.add(order)
        self.session.commit()
        
        logger.info(f"Approved purchase order {order_id}")
        return {"message": "Purchase order approved successfully"}
    
    async def deliver_purchase_order(
        self, 
        order_id: uuid.UUID, 
        delivery_date: Optional[date] = None,
        received_by: Optional[uuid.UUID] = None
    ) -> dict:
        """Mark purchase order as delivered and update stock
        
        Args:
            order_id: Purchase order UUID
            delivery_date: Actual delivery date
            received_by: User who received the order
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If order not found or cannot be delivered
        """
        order = self.session.get(PurchaseOrder, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        if order.status != PurchaseOrderStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deliver order with status {order.status}"
            )
        
        # Update order status
        order.status = PurchaseOrderStatus.DELIVERED
        order.delivery_date = delivery_date or date.today()
        order.received_by = received_by
        order.updated_at = datetime.utcnow()
        
        # Update stock quantities for all items
        order_items = self.session.exec(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == order_id)
        ).all()
        
        for order_item in order_items:
            item = self.session.get(Item, order_item.item_id)
            if item:
                item.current_quantity += order_item.quantity
                self.session.add(item)
        
        self.session.add(order)
        self.session.commit()
        
        logger.info(f"Delivered purchase order {order_id} and updated stock")
        return {"message": "Purchase order delivered and stock updated successfully"}
    
    async def cancel_purchase_order(self, order_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Cancel a purchase order
        
        Args:
            order_id: Purchase order UUID
            reason: Cancellation reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If order not found or cannot be cancelled
        """
        order = self.session.get(PurchaseOrder, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        if order.status in [PurchaseOrderStatus.DELIVERED, PurchaseOrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status}"
            )
        
        order.status = PurchaseOrderStatus.CANCELLED
        if reason:
            order.notes = f"{order.notes or ''}\nCancelled: {reason}".strip()
        order.updated_at = datetime.utcnow()
        
        self.session.add(order)
        self.session.commit()
        
        logger.info(f"Cancelled purchase order {order_id}")
        return {"message": "Purchase order cancelled successfully"}
    
    async def get_overdue_orders(self) -> List[PurchaseOrderResponse]:
        """Get overdue purchase orders
        
        Returns:
            List of overdue orders
        """
        return await self.get_purchase_orders(overdue_only=True, limit=1000)
    
    async def get_purchase_order_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        supplier_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get purchase order analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            supplier_id: Filter by specific supplier
            
        Returns:
            Analytics data
        """
        query = select(PurchaseOrder)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(PurchaseOrder.order_date >= start_date)
        if end_date:
            conditions.append(PurchaseOrder.order_date <= end_date)
        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        orders = self.session.exec(query).all()
        
        # Calculate metrics
        total_orders = len(orders)
        total_value = sum(order.total_cost or 0 for order in orders)
        
        # Status breakdown
        status_breakdown = {}
        for status in PurchaseOrderStatus:
            status_breakdown[status.value] = len([o for o in orders if o.status == status])
        
        # Average order value
        avg_order_value = total_value / total_orders if total_orders > 0 else 0
        
        # Delivery performance
        delivered_orders = [o for o in orders if o.status == PurchaseOrderStatus.DELIVERED]
        on_time_deliveries = 0
        total_delivery_days = 0
        
        for order in delivered_orders:
            if order.delivery_date and order.expected_delivery_date:
                if order.delivery_date <= order.expected_delivery_date:
                    on_time_deliveries += 1
                
                delivery_days = (order.delivery_date - order.order_date).days
                total_delivery_days += delivery_days
        
        on_time_rate = (on_time_deliveries / len(delivered_orders) * 100) if delivered_orders else 0
        avg_delivery_days = total_delivery_days / len(delivered_orders) if delivered_orders else 0
        
        # Top suppliers by order value
        supplier_values = {}
        for order in orders:
            supplier_id = str(order.supplier_id)
            if supplier_id not in supplier_values:
                supplier_values[supplier_id] = 0
            supplier_values[supplier_id] += order.total_cost or 0
        
        top_suppliers = sorted(supplier_values.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_orders": total_orders,
            "total_value": float(total_value),
            "average_order_value": float(avg_order_value),
            "status_breakdown": status_breakdown,
            "delivery_performance": {
                "on_time_rate": on_time_rate,
                "average_delivery_days": avg_delivery_days,
                "delivered_orders": len(delivered_orders)
            },
            "top_suppliers_by_value": top_suppliers,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def generate_restock_suggestions(self) -> List[Dict[str, Any]]:
        """Generate restock suggestions based on low stock levels
        
        Returns:
            List of restock suggestions
        """
        # Get items below reorder level
        low_stock_items = self.session.exec(
            select(Item).where(Item.current_quantity <= Item.reorder_level)
        ).all()
        
        suggestions = []
        
        for item in low_stock_items:
            # Calculate suggested order quantity (simple reorder formula)
            suggested_quantity = max(
                item.reorder_level * 2 - item.current_quantity,  # Bring to 2x reorder level
                item.reorder_level  # Minimum order
            )
            
            # Get supplier info
            supplier = None
            if item.supplier_id:
                supplier = self.session.get(Supplier, item.supplier_id)
            
            suggestions.append({
                "item_id": str(item.id),
                "item_name": item.name,
                "current_quantity": item.current_quantity,
                "reorder_level": item.reorder_level,
                "suggested_quantity": suggested_quantity,
                "estimated_cost": float(suggested_quantity * item.unit_cost),
                "supplier_id": str(item.supplier_id) if item.supplier_id else None,
                "supplier_name": supplier.name if supplier else None,
                "priority": "high" if item.current_quantity == 0 else "medium"
            })
        
        # Sort by priority (out of stock first, then by cost impact)
        suggestions.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1,
            -x["estimated_cost"]
        ))
        
        return suggestions
    
    async def _generate_order_number(self) -> str:
        """Generate unique order number
        
        Returns:
            Order number in format PO-YYYYMM-XXXX
        """
        today = date.today()
        prefix = f"PO-{today.strftime('%Y%m')}"
        
        # Get the last order number for this month
        last_order = self.session.exec(
            select(PurchaseOrder)
            .where(PurchaseOrder.order_number.like(f"{prefix}%"))
            .order_by(PurchaseOrder.order_number.desc())
        ).first()
        
        if last_order:
            # Extract sequence number and increment
            last_sequence = int(last_order.order_number.split('-')[-1])
            sequence = last_sequence + 1
        else:
            sequence = 1
        
        return f"{prefix}-{sequence:04d}"
    
    async def _to_response(self, order: PurchaseOrder) -> PurchaseOrderResponse:
        """Convert purchase order model to response schema
        
        Args:
            order: Purchase order model
            
        Returns:
            Purchase order response schema
        """
        # Get order items
        order_items = self.session.exec(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == order.id)
        ).all()
        
        items = []
        for order_item in order_items:
            item = self.session.get(Item, order_item.item_id)
            items.append(PurchaseOrderItemResponse(
                id=order_item.id,
                item_id=order_item.item_id,
                item_name=item.name if item else "Unknown Item",
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                total_price=order_item.total_price
            ))
        
        # Get supplier info
        supplier = self.session.get(Supplier, order.supplier_id)
        
        return PurchaseOrderResponse(
            id=order.id,
            order_number=order.order_number,
            supplier_id=order.supplier_id,
            supplier_name=supplier.name if supplier else "Unknown Supplier",
            status=order.status,
            order_date=order.order_date,
            expected_delivery_date=order.expected_delivery_date,
            delivery_date=order.delivery_date,
            total_cost=order.total_cost,
            notes=order.notes,
            created_by=order.created_by,
            approved_by=order.approved_by,
            approved_at=order.approved_at,
            received_by=order.received_by,
            items=items,
            created_at=order.created_at,
            updated_at=order.updated_at
        )