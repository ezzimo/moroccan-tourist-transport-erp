"""
Stock movement service for inventory management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.stock_movement import StockMovement, MovementType
from models.item import Item
from schemas.stock_movement import (
    StockMovementCreate, StockMovementUpdate, StockMovementResponse
)
from utils.notifications import send_low_stock_alert
from utils.validation import validate_stock_movement
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class MovementService:
    """Service for handling stock movement operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_movement(
        self, 
        movement_data: StockMovementCreate, 
        performed_by: uuid.UUID
    ) -> StockMovementResponse:
        """Create a new stock movement
        
        Args:
            movement_data: Movement creation data
            performed_by: User ID who performed the movement
            
        Returns:
            Created movement record
            
        Raises:
            HTTPException: If validation fails or item not found
        """
        # Validate item exists
        item = self.session.get(Item, movement_data.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Validate movement data
        validation_errors = validate_stock_movement(movement_data.model_dump(), item)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": validation_errors}
            )
        
        # Check stock availability for OUT movements
        if movement_data.type == MovementType.OUT:
            if item.current_quantity < movement_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {item.current_quantity}, Requested: {movement_data.quantity}"
                )
        
        # Create movement record
        movement = StockMovement(
            **movement_data.model_dump(),
            performed_by=performed_by,
            date=datetime.utcnow()
        )
        
        self.session.add(movement)
        
        # Update item quantity
        if movement_data.type == MovementType.IN:
            item.current_quantity += movement_data.quantity
        elif movement_data.type == MovementType.OUT:
            item.current_quantity -= movement_data.quantity
        elif movement_data.type == MovementType.ADJUST:
            # For adjustments, the quantity is the new total, not the change
            item.current_quantity = movement_data.quantity
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(movement)
        
        # Check for low stock alert
        if item.current_quantity <= item.reorder_level:
            try:
                await send_low_stock_alert(
                    item_id=str(item.id),
                    item_name=item.name,
                    current_quantity=item.current_quantity,
                    reorder_level=item.reorder_level,
                    supplier_id=str(item.supplier_id) if item.supplier_id else None
                )
            except Exception as e:
                logger.error(f"Failed to send low stock alert: {str(e)}")
        
        logger.info(f"Created stock movement {movement.id} for item {item.name}")
        return self._to_response(movement)
    
    async def get_movement(self, movement_id: uuid.UUID) -> StockMovementResponse:
        """Get movement by ID
        
        Args:
            movement_id: Movement UUID
            
        Returns:
            Movement details
            
        Raises:
            HTTPException: If movement not found
        """
        movement = self.session.get(StockMovement, movement_id)
        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movement not found"
            )
        
        return self._to_response(movement)
    
    async def get_movements(
        self,
        skip: int = 0,
        limit: int = 100,
        item_id: Optional[uuid.UUID] = None,
        movement_type: Optional[MovementType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        performed_by: Optional[uuid.UUID] = None,
        reference: Optional[str] = None
    ) -> List[StockMovementResponse]:
        """Get movements with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            item_id: Filter by item ID
            movement_type: Filter by movement type
            start_date: Filter movements from this date
            end_date: Filter movements until this date
            performed_by: Filter by user who performed movement
            reference: Filter by reference
            
        Returns:
            List of movements
        """
        query = select(StockMovement)
        
        # Apply filters
        conditions = []
        
        if item_id:
            conditions.append(StockMovement.item_id == item_id)
        
        if movement_type:
            conditions.append(StockMovement.type == movement_type)
        
        if start_date:
            conditions.append(StockMovement.date >= datetime.combine(start_date, datetime.min.time()))
        
        if end_date:
            conditions.append(StockMovement.date <= datetime.combine(end_date, datetime.max.time()))
        
        if performed_by:
            conditions.append(StockMovement.performed_by == performed_by)
        
        if reference:
            conditions.append(StockMovement.reference.ilike(f"%{reference}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(StockMovement.date.desc()).offset(skip).limit(limit)
        movements = self.session.exec(query).all()
        
        return [self._to_response(movement) for movement in movements]
    
    async def get_item_movements(
        self,
        item_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        movement_type: Optional[MovementType] = None
    ) -> List[StockMovementResponse]:
        """Get movements for a specific item
        
        Args:
            item_id: Item UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            movement_type: Filter by movement type
            
        Returns:
            List of item movements
        """
        return await self.get_movements(
            skip=skip,
            limit=limit,
            item_id=item_id,
            movement_type=movement_type
        )
    
    async def update_movement(
        self, 
        movement_id: uuid.UUID, 
        movement_data: StockMovementUpdate
    ) -> StockMovementResponse:
        """Update movement information
        
        Args:
            movement_id: Movement UUID
            movement_data: Update data
            
        Returns:
            Updated movement
            
        Raises:
            HTTPException: If movement not found
        """
        movement = self.session.get(StockMovement, movement_id)
        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movement not found"
            )
        
        # Only allow updating notes and reference for audit purposes
        update_data = movement_data.model_dump(exclude_unset=True)
        allowed_fields = ['notes', 'reference']
        
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(movement, field, value)
        
        self.session.add(movement)
        self.session.commit()
        self.session.refresh(movement)
        
        logger.info(f"Updated movement {movement_id}")
        return self._to_response(movement)
    
    async def delete_movement(self, movement_id: uuid.UUID) -> dict:
        """Delete a movement (admin only - reverses stock changes)
        
        Args:
            movement_id: Movement UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If movement not found
        """
        movement = self.session.get(StockMovement, movement_id)
        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movement not found"
            )
        
        # Get the item to reverse stock changes
        item = self.session.get(Item, movement.item_id)
        if item:
            # Reverse the stock movement
            if movement.type == MovementType.IN:
                item.current_quantity -= movement.quantity
            elif movement.type == MovementType.OUT:
                item.current_quantity += movement.quantity
            # For ADJUST movements, we can't easily reverse without knowing previous state
            
            # Ensure quantity doesn't go negative
            if item.current_quantity < 0:
                item.current_quantity = 0
            
            self.session.add(item)
        
        self.session.delete(movement)
        self.session.commit()
        
        logger.info(f"Deleted movement {movement_id} and reversed stock changes")
        return {"message": "Movement deleted successfully"}
    
    async def get_movement_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        item_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get movement analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            item_id: Filter by specific item
            
        Returns:
            Analytics data
        """
        query = select(StockMovement)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(StockMovement.date >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            conditions.append(StockMovement.date <= datetime.combine(end_date, datetime.max.time()))
        if item_id:
            conditions.append(StockMovement.item_id == item_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        movements = self.session.exec(query).all()
        
        # Calculate metrics
        total_movements = len(movements)
        in_movements = len([m for m in movements if m.type == MovementType.IN])
        out_movements = len([m for m in movements if m.type == MovementType.OUT])
        adjust_movements = len([m for m in movements if m.type == MovementType.ADJUST])
        
        # Calculate quantities
        total_in_quantity = sum(m.quantity for m in movements if m.type == MovementType.IN)
        total_out_quantity = sum(m.quantity for m in movements if m.type == MovementType.OUT)
        
        # Most active items
        item_activity = {}
        for movement in movements:
            item_id = str(movement.item_id)
            if item_id not in item_activity:
                item_activity[item_id] = {"in": 0, "out": 0, "total": 0}
            
            if movement.type == MovementType.IN:
                item_activity[item_id]["in"] += movement.quantity
            elif movement.type == MovementType.OUT:
                item_activity[item_id]["out"] += movement.quantity
            
            item_activity[item_id]["total"] += movement.quantity
        
        # Sort by total activity
        most_active_items = sorted(
            item_activity.items(), 
            key=lambda x: x[1]["total"], 
            reverse=True
        )[:10]
        
        return {
            "total_movements": total_movements,
            "movement_breakdown": {
                "in_movements": in_movements,
                "out_movements": out_movements,
                "adjust_movements": adjust_movements
            },
            "quantity_summary": {
                "total_in_quantity": total_in_quantity,
                "total_out_quantity": total_out_quantity,
                "net_change": total_in_quantity - total_out_quantity
            },
            "most_active_items": most_active_items,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_consumption_trends(
        self,
        item_id: uuid.UUID,
        months: int = 12
    ) -> Dict[str, Any]:
        """Get consumption trends for an item
        
        Args:
            item_id: Item UUID
            months: Number of months to analyze
            
        Returns:
            Consumption trend data
        """
        start_date = date.today() - timedelta(days=months * 30)
        
        query = select(StockMovement).where(
            and_(
                StockMovement.item_id == item_id,
                StockMovement.type == MovementType.OUT,
                StockMovement.date >= datetime.combine(start_date, datetime.min.time())
            )
        )
        
        movements = self.session.exec(query).all()
        
        # Group by month
        monthly_consumption = {}
        for movement in movements:
            month_key = movement.date.strftime("%Y-%m")
            if month_key not in monthly_consumption:
                monthly_consumption[month_key] = 0
            monthly_consumption[month_key] += movement.quantity
        
        # Calculate average consumption
        consumption_values = list(monthly_consumption.values())
        avg_monthly_consumption = sum(consumption_values) / len(consumption_values) if consumption_values else 0
        
        # Predict reorder date
        item = self.session.get(Item, item_id)
        days_until_reorder = None
        if item and avg_monthly_consumption > 0:
            monthly_rate = avg_monthly_consumption / 30  # Daily rate
            if monthly_rate > 0:
                days_until_reorder = max(0, (item.current_quantity - item.reorder_level) / monthly_rate)
        
        return {
            "item_id": str(item_id),
            "monthly_consumption": monthly_consumption,
            "average_monthly_consumption": avg_monthly_consumption,
            "predicted_days_until_reorder": days_until_reorder,
            "analysis_period_months": months
        }
    
    def _to_response(self, movement: StockMovement) -> StockMovementResponse:
        """Convert movement model to response schema
        
        Args:
            movement: Movement model
            
        Returns:
            Movement response schema
        """
        return StockMovementResponse(
            id=movement.id,
            item_id=movement.item_id,
            type=movement.type,
            quantity=movement.quantity,
            reference=movement.reference,
            notes=movement.notes,
            date=movement.date,
            performed_by=movement.performed_by,
            created_at=movement.created_at
        )