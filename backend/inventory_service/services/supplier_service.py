"""
Supplier service for supplier management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.supplier import Supplier
from models.item import Item
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierWithStats
)
from utils.validation import validate_supplier_data
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for handling supplier operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_supplier(self, supplier_data: SupplierCreate) -> SupplierResponse:
        """Create a new supplier
        
        Args:
            supplier_data: Supplier creation data
            
        Returns:
            Created supplier
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate supplier data
        validation_errors = validate_supplier_data(supplier_data.model_dump())
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": validation_errors}
            )
        
        # Check if supplier name already exists
        statement = select(Supplier).where(Supplier.name == supplier_data.name)
        existing_supplier = self.session.exec(statement).first()
        
        if existing_supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier name already exists"
            )
        
        # Create supplier
        supplier = Supplier(**supplier_data.model_dump())
        
        self.session.add(supplier)
        self.session.commit()
        self.session.refresh(supplier)
        
        logger.info(f"Created supplier {supplier.name}")
        return self._to_response(supplier)
    
    async def get_supplier(self, supplier_id: uuid.UUID) -> SupplierResponse:
        """Get supplier by ID
        
        Args:
            supplier_id: Supplier UUID
            
        Returns:
            Supplier details
            
        Raises:
            HTTPException: If supplier not found
        """
        supplier = self.session.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        return self._to_response(supplier)
    
    async def get_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = False,
        min_performance_score: Optional[float] = None
    ) -> List[SupplierResponse]:
        """Get suppliers with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search query for name or contact
            active_only: Show only active suppliers
            min_performance_score: Minimum performance score filter
            
        Returns:
            List of suppliers
        """
        query = select(Supplier)
        
        # Apply filters
        conditions = []
        
        if search:
            search_filter = or_(
                Supplier.name.ilike(f"%{search}%"),
                Supplier.contact_person.ilike(f"%{search}%"),
                Supplier.email.ilike(f"%{search}%")
            )
            conditions.append(search_filter)
        
        if active_only:
            conditions.append(Supplier.is_active == True)
        
        if min_performance_score is not None:
            conditions.append(Supplier.performance_score >= min_performance_score)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Supplier.name).offset(skip).limit(limit)
        suppliers = self.session.exec(query).all()
        
        return [self._to_response(supplier) for supplier in suppliers]
    
    async def update_supplier(
        self, 
        supplier_id: uuid.UUID, 
        supplier_data: SupplierUpdate
    ) -> SupplierResponse:
        """Update supplier information
        
        Args:
            supplier_id: Supplier UUID
            supplier_data: Update data
            
        Returns:
            Updated supplier
            
        Raises:
            HTTPException: If supplier not found
        """
        supplier = self.session.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        # Update fields
        update_data = supplier_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        
        supplier.updated_at = datetime.utcnow()
        
        self.session.add(supplier)
        self.session.commit()
        self.session.refresh(supplier)
        
        logger.info(f"Updated supplier {supplier_id}")
        return self._to_response(supplier)
    
    async def delete_supplier(self, supplier_id: uuid.UUID) -> dict:
        """Delete supplier (soft delete by marking inactive)
        
        Args:
            supplier_id: Supplier UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If supplier not found or has active items
        """
        supplier = self.session.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        # Check if supplier has active items
        active_items = self.session.exec(
            select(Item).where(Item.supplier_id == supplier_id)
        ).all()
        
        if active_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete supplier with {len(active_items)} active items"
            )
        
        supplier.is_active = False
        supplier.updated_at = datetime.utcnow()
        
        self.session.add(supplier)
        self.session.commit()
        
        logger.info(f"Deactivated supplier {supplier_id}")
        return {"message": "Supplier deactivated successfully"}
    
    async def get_supplier_with_stats(self, supplier_id: uuid.UUID) -> SupplierWithStats:
        """Get supplier with performance statistics
        
        Args:
            supplier_id: Supplier UUID
            
        Returns:
            Supplier with detailed statistics
            
        Raises:
            HTTPException: If supplier not found
        """
        supplier = self.session.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        # Get supplier items
        items = self.session.exec(
            select(Item).where(Item.supplier_id == supplier_id)
        ).all()
        
        # Get purchase orders
        purchase_orders = self.session.exec(
            select(PurchaseOrder).where(PurchaseOrder.supplier_id == supplier_id)
        ).all()
        
        # Calculate statistics
        total_items = len(items)
        total_orders = len(purchase_orders)
        completed_orders = len([po for po in purchase_orders if po.status == PurchaseOrderStatus.DELIVERED])
        
        # Calculate average delivery time
        delivered_orders = [po for po in purchase_orders if po.status == PurchaseOrderStatus.DELIVERED and po.delivery_date]
        avg_delivery_days = None
        if delivered_orders:
            delivery_times = [
                (po.delivery_date - po.order_date).days 
                for po in delivered_orders 
                if po.delivery_date and po.order_date
            ]
            if delivery_times:
                avg_delivery_days = sum(delivery_times) / len(delivery_times)
        
        # Calculate total order value
        total_order_value = sum(po.total_cost for po in purchase_orders if po.total_cost)
        
        # On-time delivery rate
        on_time_orders = 0
        if delivered_orders:
            for po in delivered_orders:
                if po.delivery_date and po.expected_delivery_date:
                    if po.delivery_date <= po.expected_delivery_date:
                        on_time_orders += 1
        
        on_time_rate = (on_time_orders / len(delivered_orders) * 100) if delivered_orders else 0
        
        return SupplierWithStats(
            **self._to_response(supplier).model_dump(),
            total_items_supplied=total_items,
            total_purchase_orders=total_orders,
            completed_orders=completed_orders,
            average_delivery_days=avg_delivery_days,
            total_order_value=total_order_value,
            on_time_delivery_rate=on_time_rate,
            order_completion_rate=(completed_orders / total_orders * 100) if total_orders > 0 else 0
        )
    
    async def update_performance_score(
        self, 
        supplier_id: uuid.UUID, 
        score: float,
        notes: Optional[str] = None
    ) -> dict:
        """Update supplier performance score
        
        Args:
            supplier_id: Supplier UUID
            score: Performance score (0-100)
            notes: Performance notes
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If supplier not found or invalid score
        """
        supplier = self.session.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        if not (0 <= score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Performance score must be between 0 and 100"
            )
        
        supplier.performance_score = score
        if notes:
            supplier.notes = notes
        supplier.updated_at = datetime.utcnow()
        
        self.session.add(supplier)
        self.session.commit()
        
        logger.info(f"Updated performance score for supplier {supplier_id}: {score}")
        return {"message": "Performance score updated successfully"}
    
    async def get_supplier_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get supplier analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Analytics data
        """
        # Get all suppliers
        suppliers = self.session.exec(select(Supplier)).all()
        
        # Get purchase orders in date range
        po_query = select(PurchaseOrder)
        if start_date:
            po_query = po_query.where(PurchaseOrder.order_date >= start_date)
        if end_date:
            po_query = po_query.where(PurchaseOrder.order_date <= end_date)
        
        purchase_orders = self.session.exec(po_query).all()
        
        # Calculate metrics
        total_suppliers = len(suppliers)
        active_suppliers = len([s for s in suppliers if s.is_active])
        
        # Performance distribution
        performance_ranges = {
            "excellent": len([s for s in suppliers if s.performance_score and s.performance_score >= 90]),
            "good": len([s for s in suppliers if s.performance_score and 70 <= s.performance_score < 90]),
            "average": len([s for s in suppliers if s.performance_score and 50 <= s.performance_score < 70]),
            "poor": len([s for s in suppliers if s.performance_score and s.performance_score < 50]),
            "unrated": len([s for s in suppliers if not s.performance_score])
        }
        
        # Top suppliers by order value
        supplier_order_values = {}
        for po in purchase_orders:
            supplier_id = str(po.supplier_id)
            if supplier_id not in supplier_order_values:
                supplier_order_values[supplier_id] = 0
            supplier_order_values[supplier_id] += po.total_cost or 0
        
        top_suppliers = sorted(
            supplier_order_values.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Average delivery performance
        delivered_orders = [po for po in purchase_orders if po.status == PurchaseOrderStatus.DELIVERED]
        avg_delivery_time = None
        if delivered_orders:
            delivery_times = [
                (po.delivery_date - po.order_date).days
                for po in delivered_orders
                if po.delivery_date and po.order_date
            ]
            if delivery_times:
                avg_delivery_time = sum(delivery_times) / len(delivery_times)
        
        return {
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
            "performance_distribution": performance_ranges,
            "top_suppliers_by_value": top_suppliers,
            "average_delivery_time_days": avg_delivery_time,
            "total_purchase_orders": len(purchase_orders),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_supplier_recommendations(self) -> List[Dict[str, Any]]:
        """Get supplier performance recommendations
        
        Returns:
            List of recommendations
        """
        suppliers = self.session.exec(select(Supplier).where(Supplier.is_active == True)).all()
        recommendations = []
        
        for supplier in suppliers:
            # Get supplier stats
            stats = await self.get_supplier_with_stats(supplier.id)
            
            # Generate recommendations based on performance
            if stats.performance_score and stats.performance_score < 50:
                recommendations.append({
                    "supplier_id": str(supplier.id),
                    "supplier_name": supplier.name,
                    "type": "performance_review",
                    "priority": "high",
                    "message": f"Supplier has low performance score ({stats.performance_score}%). Consider review or replacement."
                })
            
            if stats.on_time_delivery_rate < 70:
                recommendations.append({
                    "supplier_id": str(supplier.id),
                    "supplier_name": supplier.name,
                    "type": "delivery_improvement",
                    "priority": "medium",
                    "message": f"On-time delivery rate is {stats.on_time_delivery_rate:.1f}%. Discuss delivery improvements."
                })
            
            if stats.average_delivery_days and stats.average_delivery_days > supplier.average_delivery_time:
                recommendations.append({
                    "supplier_id": str(supplier.id),
                    "supplier_name": supplier.name,
                    "type": "delivery_delay",
                    "priority": "medium",
                    "message": f"Average delivery time ({stats.average_delivery_days:.1f} days) exceeds expected ({supplier.average_delivery_time} days)."
                })
        
        return recommendations
    
    def _to_response(self, supplier: Supplier) -> SupplierResponse:
        """Convert supplier model to response schema
        
        Args:
            supplier: Supplier model
            
        Returns:
            Supplier response schema
        """
        return SupplierResponse(
            id=supplier.id,
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            payment_terms=supplier.payment_terms,
            average_delivery_time=supplier.average_delivery_time,
            performance_score=supplier.performance_score,
            is_active=supplier.is_active,
            notes=supplier.notes,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at
        )