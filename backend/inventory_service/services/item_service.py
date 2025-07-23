"""
Item service for inventory item management
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.item import Item, ItemStatus
from models.stock_movement import StockMovement, MovementType, MovementReason
from schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemSummary,
    ItemSearch, ItemStockAdjustment, ItemReorderSuggestion
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import redis
import uuid


class ItemService:
    """Service for handling item operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_item(self, item_data: ItemCreate) -> ItemResponse:
        """Create a new inventory item"""
        # Check if SKU already exists
        statement = select(Item).where(Item.sku == item_data.sku)
        existing_item = self.session.exec(statement).first()
        
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )
        
        # Create item
        item = Item(**item_data.model_dump())
        item.average_cost = item.unit_cost
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Create initial stock movement if quantity > 0
        if item.current_quantity > 0:
            await self._create_initial_stock_movement(item)
        
        # Send low stock alert if applicable
        await self._check_and_send_alerts(item)
        
        return self._create_item_response(item)
    
    async def get_item(self, item_id: uuid.UUID) -> ItemResponse:
        """Get item by ID"""
        statement = select(Item).where(Item.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        return self._create_item_response(item)
    
    async def get_items(
        self, 
        pagination: PaginationParams,
        search: Optional[ItemSearch] = None
    ) -> Tuple[List[ItemResponse], int]:
        """Get list of items with optional search"""
        query = select(Item)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Item.name.ilike(search_term),
                        Item.sku.ilike(search_term),
                        Item.description.ilike(search_term),
                        Item.barcode.ilike(search_term)
                    )
                )
            
            if search.category:
                conditions.append(Item.category == search.category)
            
            if search.status:
                conditions.append(Item.status == search.status)
            
            if search.warehouse_location:
                conditions.append(Item.warehouse_location.ilike(f"%{search.warehouse_location}%"))
            
            if search.supplier_id:
                conditions.append(Item.primary_supplier_id == search.supplier_id)
            
            if search.is_low_stock is not None:
                if search.is_low_stock:
                    conditions.append(Item.current_quantity <= Item.reorder_level)
                else:
                    conditions.append(Item.current_quantity > Item.reorder_level)
            
            if search.is_critical is not None:
                conditions.append(Item.is_critical == search.is_critical)
            
            if search.has_expiry is not None:
                conditions.append(Item.has_expiry == search.has_expiry)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by name
        query = query.order_by(Item.name)
        
        items, total = paginate_query(self.session, query, pagination)
        
        return [self._create_item_response(item) for item in items], total
    
    async def update_item(self, item_id: uuid.UUID, item_data: ItemUpdate) -> ItemResponse:
        """Update item information"""
        statement = select(Item).where(Item.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Update fields
        update_data = item_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.utcnow()
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Check for alerts after update
        await self._check_and_send_alerts(item)
        
        return self._create_item_response(item)
    
    async def adjust_stock(
        self, 
        item_id: uuid.UUID, 
        adjustment: ItemStockAdjustment,
        performed_by: uuid.UUID
    ) -> ItemResponse:
        """Adjust item stock quantity"""
        statement = select(Item).where(Item.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Validate adjustment
        new_quantity = item.current_quantity + adjustment.quantity
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adjustment would result in negative stock"
            )
        
        # Create stock movement
        movement = StockMovement(
            item_id=item_id,
            movement_type=MovementType.ADJUST,
            reason=MovementReason.ADJUSTMENT,
            quantity=abs(adjustment.quantity),
            quantity_before=item.current_quantity,
            quantity_after=new_quantity,
            notes=adjustment.notes,
            reference_number=adjustment.reference_number,
            performed_by=performed_by
        )
        
        # Update item quantity
        item.current_quantity = new_quantity
        item.updated_at = datetime.utcnow()
        
        self.session.add(movement)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Check for alerts
        await self._check_and_send_alerts(item)
        
        return self._create_item_response(item)
    
    async def delete_item(self, item_id: uuid.UUID) -> dict:
        """Delete item (soft delete by marking inactive)"""
        statement = select(Item).where(Item.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Check if item has stock movements
        movements_stmt = select(StockMovement).where(StockMovement.item_id == item_id).limit(1)
        has_movements = self.session.exec(movements_stmt).first()
        
        if has_movements:
            # Soft delete - mark as inactive
            item.status = ItemStatus.INACTIVE
            item.updated_at = datetime.utcnow()
            self.session.add(item)
            self.session.commit()
            
            return {"message": "Item deactivated successfully (has movement history)"}
        else:
            # Hard delete if no movements
            self.session.delete(item)
            self.session.commit()
            
            return {"message": "Item deleted successfully"}
    
    async def get_items_summary(self) -> ItemSummary:
        """Get inventory summary statistics"""
        # Total items
        total_stmt = select(func.count(Item.id))
        total_items = self.session.exec(total_stmt).one()
        
        # Active items
        active_stmt = select(func.count(Item.id)).where(Item.status == ItemStatus.ACTIVE)
        active_items = self.session.exec(active_stmt).one()
        
        # Low stock items
        low_stock_stmt = select(func.count(Item.id)).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.current_quantity <= Item.reorder_level
            )
        )
        low_stock_items = self.session.exec(low_stock_stmt).one()
        
        # Out of stock items
        out_of_stock_stmt = select(func.count(Item.id)).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.current_quantity <= 0
            )
        )
        out_of_stock_items = self.session.exec(out_of_stock_stmt).one()
        
        # Expired items
        expired_stmt = select(func.count(Item.id)).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.has_expiry == True,
                Item.expiry_date < date.today()
            )
        )
        expired_items = self.session.exec(expired_stmt).one()
        
        # Total stock value
        value_stmt = select(func.sum(Item.current_quantity * Item.unit_cost)).where(
            Item.status == ItemStatus.ACTIVE
        )
        total_stock_value = self.session.exec(value_stmt).one() or Decimal(0)
        
        # By category
        category_stmt = select(Item.category, func.count(Item.id)).where(
            Item.status == ItemStatus.ACTIVE
        ).group_by(Item.category)
        
        by_category = {}
        for category, count in self.session.exec(category_stmt):
            by_category[category.value] = count
        
        # By warehouse
        warehouse_stmt = select(Item.warehouse_location, func.count(Item.id)).where(
            Item.status == ItemStatus.ACTIVE
        ).group_by(Item.warehouse_location)
        
        by_warehouse = {}
        for warehouse, count in self.session.exec(warehouse_stmt):
            by_warehouse[warehouse] = count
        
        # Critical items with low stock
        critical_low_stock_stmt = select(func.count(Item.id)).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.is_critical == True,
                Item.current_quantity <= Item.reorder_level
            )
        )
        critical_items_low_stock = self.session.exec(critical_low_stock_stmt).one()
        
        return ItemSummary(
            total_items=total_items,
            active_items=active_items,
            low_stock_items=low_stock_items,
            out_of_stock_items=out_of_stock_items,
            expired_items=expired_items,
            total_stock_value=total_stock_value,
            by_category=by_category,
            by_warehouse=by_warehouse,
            critical_items_low_stock=critical_items_low_stock
        )
    
    async def get_low_stock_items(self) -> List[ItemResponse]:
        """Get all items with low stock levels"""
        statement = select(Item).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.current_quantity <= Item.reorder_level
            )
        ).order_by(Item.current_quantity / Item.reorder_level)  # Most critical first
        
        items = self.session.exec(statement).all()
        
        return [self._create_item_response(item) for item in items]
    
    async def get_reorder_suggestions(self) -> List[ItemReorderSuggestion]:
        """Get reorder suggestions for low stock items"""
        statement = select(Item).where(
            and_(
                Item.status == ItemStatus.ACTIVE,
                Item.current_quantity <= Item.reorder_level
            )
        ).order_by(Item.is_critical.desc(), Item.current_quantity / Item.reorder_level)
        
        items = self.session.exec(statement).all()
        
        suggestions = []
        for item in items:
            # Calculate suggested quantity (reorder to max level or 2x reorder level)
            if item.max_stock_level:
                suggested_quantity = item.max_stock_level - item.current_quantity
            else:
                suggested_quantity = (item.reorder_level * 2) - item.current_quantity
            
            # Determine priority
            stock_ratio = item.current_quantity / item.reorder_level if item.reorder_level > 0 else 0
            if item.is_critical and stock_ratio <= 0.1:
                priority = "Critical"
            elif stock_ratio <= 0.2:
                priority = "High"
            elif stock_ratio <= 0.5:
                priority = "Normal"
            else:
                priority = "Low"
            
            # Get supplier info
            supplier_name = None
            if item.supplier:
                supplier_name = item.supplier.name
            
            suggestions.append(ItemReorderSuggestion(
                item_id=item.id,
                item_name=item.name,
                current_quantity=item.current_quantity,
                reorder_level=item.reorder_level,
                suggested_quantity=suggested_quantity,
                primary_supplier_name=supplier_name,
                estimated_cost=suggested_quantity * item.unit_cost,
                priority=priority
            ))
        
        return suggestions
    
    async def get_item_movements(self, item_id: uuid.UUID, limit: int = 50) -> List[dict]:
        """Get stock movement history for an item"""
        statement = select(StockMovement).where(
            StockMovement.item_id == item_id
        ).order_by(StockMovement.movement_date.desc()).limit(limit)
        
        movements = self.session.exec(statement).all()
        
        return [
            {
                "id": str(movement.id),
                "movement_type": movement.movement_type.value,
                "reason": movement.reason.value,
                "quantity": movement.quantity,
                "quantity_before": movement.quantity_before,
                "quantity_after": movement.quantity_after,
                "unit_cost": movement.unit_cost,
                "total_cost": movement.total_cost,
                "reference_type": movement.reference_type,
                "reference_number": movement.reference_number,
                "notes": movement.notes,
                "movement_date": movement.movement_date.isoformat(),
                "performed_by": str(movement.performed_by)
            }
            for movement in movements
        ]
    
    async def get_items_by_category(self, category: str) -> List[ItemResponse]:
        """Get all items in a specific category"""
        statement = select(Item).where(
            and_(
                Item.category == category,
                Item.status == ItemStatus.ACTIVE
            )
        ).order_by(Item.name)
        
        items = self.session.exec(statement).all()
        
        return [self._create_item_response(item) for item in items]
    
    async def get_items_by_warehouse(self, warehouse: str) -> List[ItemResponse]:
        """Get all items in a specific warehouse"""
        statement = select(Item).where(
            and_(
                Item.warehouse_location.ilike(f"%{warehouse}%"),
                Item.status == ItemStatus.ACTIVE
            )
        ).order_by(Item.name)
        
        items = self.session.exec(statement).all()
        
        return [self._create_item_response(item) for item in items]
    
    async def _create_initial_stock_movement(self, item: Item):
        """Create initial stock movement for new item with quantity"""
        movement = StockMovement(
            item_id=item.id,
            movement_type=MovementType.IN,
            reason=MovementReason.INITIAL_STOCK,
            quantity=item.current_quantity,
            unit_cost=item.unit_cost,
            quantity_before=Decimal(0),
            quantity_after=item.current_quantity,
            notes="Initial stock entry",
            performed_by=uuid.uuid4()  # System user
        )
        movement.calculate_total_cost()
        
        self.session.add(movement)
        self.session.commit()
    
    async def _check_and_send_alerts(self, item: Item):
        """Check and send alerts for low stock, expiry, etc."""
        alerts = []
        
        # Low stock alert
        if item.is_low_stock():
            alerts.append({
                "type": "low_stock",
                "item_id": str(item.id),
                "item_name": item.name,
                "current_quantity": item.current_quantity,
                "reorder_level": item.reorder_level,
                "is_critical": item.is_critical
            })
        
        # Expiry alert
        if item.has_expiry and item.expiry_date:
            days_until_expiry = item.days_until_expiry()
            if days_until_expiry is not None and days_until_expiry <= 30:
                alerts.append({
                    "type": "expiry_warning",
                    "item_id": str(item.id),
                    "item_name": item.name,
                    "expiry_date": item.expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry
                })
        
        # Store alerts in Redis for real-time notifications
        if alerts:
            for alert in alerts:
                self.redis.lpush("inventory_alerts", str(alert))
                self.redis.expire("inventory_alerts", 86400)  # 24 hours
    
    def _create_item_response(self, item: Item) -> ItemResponse:
        """Create item response with calculated fields"""
        return ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            sku=item.sku,
            barcode=item.barcode,
            category=item.category,
            subcategory=item.subcategory,
            brand=item.brand,
            model=item.model,
            unit=item.unit,
            unit_cost=item.unit_cost,
            currency=item.currency,
            current_quantity=item.current_quantity,
            reserved_quantity=item.reserved_quantity,
            reorder_level=item.reorder_level,
            max_stock_level=item.max_stock_level,
            warehouse_location=item.warehouse_location,
            bin_location=item.bin_location,
            primary_supplier_id=item.primary_supplier_id,
            last_purchase_date=item.last_purchase_date,
            last_purchase_cost=item.last_purchase_cost,
            average_cost=item.average_cost,
            has_expiry=item.has_expiry,
            shelf_life_days=item.shelf_life_days,
            expiry_date=item.expiry_date,
            status=item.status,
            is_critical=item.is_critical,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
            available_quantity=item.get_available_quantity(),
            is_low_stock=item.is_low_stock(),
            is_out_of_stock=item.is_out_of_stock(),
            stock_value=item.get_stock_value(),
            is_expired=item.is_expired(),
            days_until_expiry=item.days_until_expiry()
        )