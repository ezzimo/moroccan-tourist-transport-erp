"""
Database models for the fleet management microservice
"""
from .vehicle import Vehicle, VehicleType, VehicleStatus, FuelType
from .maintenance_record import MaintenanceRecord, MaintenanceType
from .assignment import Assignment, AssignmentStatus
from .fuel_log import FuelLog
from .document import Document, DocumentType

__all__ = [
    "Vehicle", "VehicleType", "VehicleStatus", "FuelType",
    "MaintenanceRecord", "MaintenanceType",
    "Assignment", "AssignmentStatus",
    "FuelLog",
    "Document", "DocumentType"
]