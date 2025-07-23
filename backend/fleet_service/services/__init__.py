"""
Service layer for business logic
"""
from .vehicle_service import VehicleService
from .maintenance_service import MaintenanceService
from .assignment_service import AssignmentService
from .fuel_service import FuelService
from .document_service import DocumentService

__all__ = ["VehicleService", "MaintenanceService", "AssignmentService", "FuelService", "DocumentService"]