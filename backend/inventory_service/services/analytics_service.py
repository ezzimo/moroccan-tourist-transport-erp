"""
Analytics service for inventory analytics and reporting
"""
from sqlmodel import Session, select, and_, or_, func
from models.item import Item, ItemCategory
from models.stock_movement import StockMovement, MovementType
from models.supplier import Supplier
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for inventory analytics and reporting"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_inventory_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive inventory dashboard data
        
        Returns:
            Dashboard metrics and KPIs
        """
        # Basic inventory metrics
        total_items = self.session.exec(select(func.count(Item.id))).first()
        low_stock_items = self.session.exec(
            select(func.count(Item.id)).where(Item.current_quantity <= Item.reorder_level)
        ).first()
        out_of_stock_items = self.session.exec(
            select(func.count(Item.id)).where(Item.current_quantity == 0)
        ).first()
        
        # Total inventory value
        items = self.session.exec(select(Item)).all()
        total_value = sum(item.current_quantity * item.unit_cost for item in items)
        
        # Recent movements (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_movements = self.session.exec(
            select(func.count(StockMovement.id))
            .where(StockMovement.date >= thirty_days_ago)
        ).first()
        
        # Pending purchase orders
        pending_orders = self.session.exec(
            select(func.count(PurchaseOrder.id))
            .where(PurchaseOrder.status == PurchaseOrderStatus.PENDING)
        ).first()
        
        # Active suppliers
        active_suppliers = self.session.exec(
            select(func.count(Supplier.id)).where(Supplier.is_active == True)
        ).first()
        
        return {
            "inventory_overview": {
                "total_items": total_items or 0,
                "low_stock_items": low_stock_items or 0,
                "out_of_stock_items": out_of_stock_items or 0,
                "total_inventory_value": float(total_value)
            },
            "activity_metrics": {
                "recent_movements": recent_movements or 0,
                "pending_orders": pending_orders or 0,
                "active_suppliers": active_suppliers or 0
            },
            "alerts": {
                "critical_stock": out_of_stock_items or 0,
                "low_stock_warnings": (low_stock_items or 0) - (out_of_stock_items or 0)
            }
        }
    
    async def get_stock_valuation_report(
        self,
        category: Optional[ItemCategory] = None,
        warehouse_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get stock valuation report
        
        Args:
            category: Filter by item category
            warehouse_location: Filter by warehouse location
            
        Returns:
            Stock valuation data
        """
        query = select(Item)
        
        # Apply filters
        conditions = []
        if category:
            conditions.append(Item.category == category)
        if warehouse_location:
            conditions.append(Item.warehouse_location == warehouse_location)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        items = self.session.exec(query).all()
        
        # Calculate valuation by category
        category_valuation = {}
        total_value = Decimal('0.00')
        total_quantity = 0
        
        for item in items:
            item_value = item.current_quantity * item.unit_cost
            total_value += item_value
            total_quantity += item.current_quantity
            
            category_name = item.category.value if item.category else "Uncategorized"
            if category_name not in category_valuation:
                category_valuation[category_name] = {
                    "items_count": 0,
                    "total_quantity": 0,
                    "total_value": Decimal('0.00'),
                    "average_unit_cost": Decimal('0.00')
                }
            
            category_valuation[category_name]["items_count"] += 1
            category_valuation[category_name]["total_quantity"] += item.current_quantity
            category_valuation[category_name]["total_value"] += item_value
        
        # Calculate average unit costs
        for category_data in category_valuation.values():
            if category_data["total_quantity"] > 0:
                category_data["average_unit_cost"] = category_data["total_value"] / category_data["total_quantity"]
        
        # Convert Decimal to float for JSON serialization
        for category_data in category_valuation.values():
            category_data["total_value"] = float(category_data["total_value"])
            category_data["average_unit_cost"] = float(category_data["average_unit_cost"])
        
        # Top 10 most valuable items
        top_items = sorted(
            [(item, item.current_quantity * item.unit_cost) for item in items],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_items_data = [
            {
                "item_id": str(item.id),
                "item_name": item.name,
                "quantity": item.current_quantity,
                "unit_cost": float(item.unit_cost),
                "total_value": float(value)
            }
            for item, value in top_items
        ]
        
        return {
            "summary": {
                "total_items": len(items),
                "total_quantity": total_quantity,
                "total_value": float(total_value),
                "average_item_value": float(total_value / len(items)) if items else 0
            },
            "by_category": category_valuation,
            "top_valuable_items": top_items_data,
            "filters_applied": {
                "category": category.value if category else None,
                "warehouse_location": warehouse_location
            }
        }
    
    async def get_movement_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movement_type: Optional[MovementType] = None
    ) -> Dict[str, Any]:
        """Get stock movement analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            movement_type: Filter by movement type
            
        Returns:
            Movement analytics data
        """
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        query = select(StockMovement).where(
            and_(
                StockMovement.date >= datetime.combine(start_date, datetime.min.time()),
                StockMovement.date <= datetime.combine(end_date, datetime.max.time())
            )
        )
        
        if movement_type:
            query = query.where(StockMovement.type == movement_type)
        
        movements = self.session.exec(query).all()
        
        # Daily movement trends
        daily_movements = {}
        current_date = start_date
        while current_date <= end_date:
            daily_movements[current_date.isoformat()] = {
                "in": 0,
                "out": 0,
                "adjust": 0,
                "total": 0
            }
            current_date += timedelta(days=1)
        
        # Populate daily data
        for movement in movements:
            movement_date = movement.date.date().isoformat()
            if movement_date in daily_movements:
                movement_type_key = movement.type.value.lower()
                daily_movements[movement_date][movement_type_key] += movement.quantity
                daily_movements[movement_date]["total"] += movement.quantity
        
        # Movement type breakdown
        type_breakdown = {
            "IN": len([m for m in movements if m.type == MovementType.IN]),
            "OUT": len([m for m in movements if m.type == MovementType.OUT]),
            "ADJUST": len([m for m in movements if m.type == MovementType.ADJUST])
        }
        
        # Most active items
        item_activity = {}
        for movement in movements:
            item_id = str(movement.item_id)
            if item_id not in item_activity:
                item_activity[item_id] = {"movements": 0, "total_quantity": 0}
            item_activity[item_id]["movements"] += 1
            item_activity[item_id]["total_quantity"] += movement.quantity
        
        # Get item names for top active items
        top_active_items = sorted(
            item_activity.items(),
            key=lambda x: x[1]["movements"],
            reverse=True
        )[:10]
        
        top_items_with_names = []
        for item_id, activity in top_active_items:
            item = self.session.get(Item, uuid.UUID(item_id))
            top_items_with_names.append({
                "item_id": item_id,
                "item_name": item.name if item else "Unknown",
                "movements_count": activity["movements"],
                "total_quantity": activity["total_quantity"]
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days + 1
            },
            "summary": {
                "total_movements": len(movements),
                "total_quantity_moved": sum(m.quantity for m in movements),
                "average_daily_movements": len(movements) / ((end_date - start_date).days + 1)
            },
            "type_breakdown": type_breakdown,
            "daily_trends": daily_movements,
            "most_active_items": top_items_with_names
        }
    
    async def get_supplier_performance_report(self) -> Dict[str, Any]:
        """Get supplier performance analytics
        
        Returns:
            Supplier performance data
        """
        suppliers = self.session.exec(select(Supplier)).all()
        
        supplier_metrics = []
        
        for supplier in suppliers:
            # Get purchase orders for this supplier
            orders = self.session.exec(
                select(PurchaseOrder).where(PurchaseOrder.supplier_id == supplier.id)
            ).all()
            
            # Calculate metrics
            total_orders = len(orders)
            delivered_orders = [o for o in orders if o.status == PurchaseOrderStatus.DELIVERED]
            pending_orders = [o for o in orders if o.status == PurchaseOrderStatus.PENDING]
            
            # Delivery performance
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
            
            # Financial metrics
            total_order_value = sum(o.total_cost or 0 for o in orders)
            avg_order_value = total_order_value / total_orders if total_orders > 0 else 0
            
            # Items supplied
            items_count = self.session.exec(
                select(func.count(Item.id)).where(Item.supplier_id == supplier.id)
            ).first() or 0
            
            supplier_metrics.append({
                "supplier_id": str(supplier.id),
                "supplier_name": supplier.name,
                "performance_score": supplier.performance_score,
                "is_active": supplier.is_active,
                "total_orders": total_orders,
                "delivered_orders": len(delivered_orders),
                "pending_orders": len(pending_orders),
                "on_time_delivery_rate": round(on_time_rate, 2),
                "average_delivery_days": round(avg_delivery_days, 1),
                "total_order_value": float(total_order_value),
                "average_order_value": float(avg_order_value),
                "items_supplied": items_count
            })
        
        # Sort by performance score
        supplier_metrics.sort(key=lambda x: x["performance_score"] or 0, reverse=True)
        
        # Overall statistics
        active_suppliers = len([s for s in suppliers if s.is_active])
        avg_performance = sum(s.performance_score or 0 for s in suppliers) / len(suppliers) if suppliers else 0
        
        return {
            "summary": {
                "total_suppliers": len(suppliers),
                "active_suppliers": active_suppliers,
                "average_performance_score": round(avg_performance, 2)
            },
            "supplier_metrics": supplier_metrics,
            "performance_distribution": {
                "excellent": len([s for s in suppliers if s.performance_score and s.performance_score >= 90]),
                "good": len([s for s in suppliers if s.performance_score and 70 <= s.performance_score < 90]),
                "average": len([s for s in suppliers if s.performance_score and 50 <= s.performance_score < 70]),
                "poor": len([s for s in suppliers if s.performance_score and s.performance_score < 50]),
                "unrated": len([s for s in suppliers if not s.performance_score])
            }
        }
    
    async def get_reorder_analysis(self) -> Dict[str, Any]:
        """Get reorder level analysis and recommendations
        
        Returns:
            Reorder analysis data
        """
        items = self.session.exec(select(Item)).all()
        
        # Categorize items by stock status
        stock_status = {
            "out_of_stock": [],
            "critical_low": [],
            "low_stock": [],
            "adequate": [],
            "overstocked": []
        }
        
        for item in items:
            if item.current_quantity == 0:
                stock_status["out_of_stock"].append(item)
            elif item.current_quantity < item.reorder_level * 0.5:
                stock_status["critical_low"].append(item)
            elif item.current_quantity <= item.reorder_level:
                stock_status["low_stock"].append(item)
            elif item.current_quantity > item.reorder_level * 3:
                stock_status["overstocked"].append(item)
            else:
                stock_status["adequate"].append(item)
        
        # Calculate reorder recommendations
        reorder_recommendations = []
        
        for category in ["out_of_stock", "critical_low", "low_stock"]:
            for item in stock_status[category]:
                # Simple reorder calculation
                suggested_quantity = max(
                    item.reorder_level * 2 - item.current_quantity,
                    item.reorder_level
                )
                
                estimated_cost = suggested_quantity * item.unit_cost
                
                # Get supplier info
                supplier = None
                if item.supplier_id:
                    supplier = self.session.get(Supplier, item.supplier_id)
                
                priority = "urgent" if category == "out_of_stock" else "high" if category == "critical_low" else "medium"
                
                reorder_recommendations.append({
                    "item_id": str(item.id),
                    "item_name": item.name,
                    "category": item.category.value if item.category else "Uncategorized",
                    "current_quantity": item.current_quantity,
                    "reorder_level": item.reorder_level,
                    "suggested_quantity": suggested_quantity,
                    "estimated_cost": float(estimated_cost),
                    "supplier_id": str(item.supplier_id) if item.supplier_id else None,
                    "supplier_name": supplier.name if supplier else None,
                    "priority": priority,
                    "stock_status": category
                })
        
        # Sort by priority and cost impact
        priority_order = {"urgent": 0, "high": 1, "medium": 2}
        reorder_recommendations.sort(key=lambda x: (
            priority_order[x["priority"]],
            -x["estimated_cost"]
        ))
        
        # Calculate total reorder cost
        total_reorder_cost = sum(rec["estimated_cost"] for rec in reorder_recommendations)
        
        return {
            "stock_status_summary": {
                "out_of_stock": len(stock_status["out_of_stock"]),
                "critical_low": len(stock_status["critical_low"]),
                "low_stock": len(stock_status["low_stock"]),
                "adequate": len(stock_status["adequate"]),
                "overstocked": len(stock_status["overstocked"])
            },
            "reorder_recommendations": reorder_recommendations,
            "financial_impact": {
                "total_reorder_cost": float(total_reorder_cost),
                "urgent_items_cost": float(sum(
                    rec["estimated_cost"] for rec in reorder_recommendations 
                    if rec["priority"] == "urgent"
                )),
                "high_priority_cost": float(sum(
                    rec["estimated_cost"] for rec in reorder_recommendations 
                    if rec["priority"] == "high"
                ))
            }
        }
    
    async def get_consumption_forecast(
        self,
        item_id: Optional[uuid.UUID] = None,
        months_ahead: int = 3
    ) -> Dict[str, Any]:
        """Get consumption forecast based on historical data
        
        Args:
            item_id: Specific item to forecast (if None, forecasts for all items)
            months_ahead: Number of months to forecast
            
        Returns:
            Consumption forecast data
        """
        # Get historical movement data (last 12 months)
        twelve_months_ago = date.today() - timedelta(days=365)
        
        query = select(StockMovement).where(
            and_(
                StockMovement.type == MovementType.OUT,
                StockMovement.date >= datetime.combine(twelve_months_ago, datetime.min.time())
            )
        )
        
        if item_id:
            query = query.where(StockMovement.item_id == item_id)
        
        movements = self.session.exec(query).all()
        
        # Group by item and month
        item_consumption = {}
        
        for movement in movements:
            item_key = str(movement.item_id)
            month_key = movement.date.strftime("%Y-%m")
            
            if item_key not in item_consumption:
                item_consumption[item_key] = {}
            
            if month_key not in item_consumption[item_key]:
                item_consumption[item_key][month_key] = 0
            
            item_consumption[item_key][month_key] += movement.quantity
        
        # Generate forecasts
        forecasts = []
        
        for item_key, monthly_data in item_consumption.items():
            item = self.session.get(Item, uuid.UUID(item_key))
            if not item:
                continue
            
            # Calculate average monthly consumption
            consumption_values = list(monthly_data.values())
            if not consumption_values:
                continue
            
            avg_monthly_consumption = sum(consumption_values) / len(consumption_values)
            
            # Simple trend analysis (last 3 months vs previous 3 months)
            recent_months = consumption_values[-3:] if len(consumption_values) >= 3 else consumption_values
            earlier_months = consumption_values[-6:-3] if len(consumption_values) >= 6 else consumption_values[:-3]
            
            trend_factor = 1.0
            if recent_months and earlier_months:
                recent_avg = sum(recent_months) / len(recent_months)
                earlier_avg = sum(earlier_months) / len(earlier_months)
                if earlier_avg > 0:
                    trend_factor = recent_avg / earlier_avg
            
            # Generate monthly forecasts
            monthly_forecasts = []
            for month in range(1, months_ahead + 1):
                # Apply trend factor with diminishing effect over time
                trend_adjustment = 1 + (trend_factor - 1) * (0.8 ** month)
                forecasted_consumption = avg_monthly_consumption * trend_adjustment
                
                monthly_forecasts.append({
                    "month": month,
                    "forecasted_consumption": round(forecasted_consumption, 2)
                })
            
            # Calculate when reorder will be needed
            current_stock = item.current_quantity
            months_until_reorder = None
            
            cumulative_consumption = 0
            for forecast in monthly_forecasts:
                cumulative_consumption += forecast["forecasted_consumption"]
                if current_stock - cumulative_consumption <= item.reorder_level:
                    months_until_reorder = forecast["month"]
                    break
            
            forecasts.append({
                "item_id": item_key,
                "item_name": item.name,
                "current_quantity": current_stock,
                "reorder_level": item.reorder_level,
                "average_monthly_consumption": round(avg_monthly_consumption, 2),
                "trend_factor": round(trend_factor, 3),
                "monthly_forecasts": monthly_forecasts,
                "months_until_reorder": months_until_reorder,
                "total_forecasted_consumption": round(sum(f["forecasted_consumption"] for f in monthly_forecasts), 2)
            })
        
        # Sort by urgency (items needing reorder soonest first)
        forecasts.sort(key=lambda x: x["months_until_reorder"] or float('inf'))
        
        return {
            "forecast_period_months": months_ahead,
            "items_analyzed": len(forecasts),
            "forecasts": forecasts,
            "summary": {
                "items_needing_reorder_soon": len([f for f in forecasts if f["months_until_reorder"] and f["months_until_reorder"] <= 1]),
                "items_with_increasing_trend": len([f for f in forecasts if f["trend_factor"] > 1.1]),
                "items_with_decreasing_trend": len([f for f in forecasts if f["trend_factor"] < 0.9])
            }
        }