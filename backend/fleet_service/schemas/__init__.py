"""
Pydantic schemas for request/response models
"""
from .vehicle import *
from .maintenance_record import *
from .assignment import *
from .fuel_log import *
from .document import *

__all__ = [
    "VehicleCreate", "VehicleUpdate", "VehicleResponse", "VehicleSummary",
    "MaintenanceRecordCreate", "MaintenanceRecordUpdate", "MaintenanceRecordResponse",
    "AssignmentCreate", "AssignmentUpdate", "AssignmentResponse",
    "FuelLogCreate", "FuelLogUpdate", "FuelLogResponse",
    "DocumentCreate", "DocumentUpdate", "DocumentResponse"
]