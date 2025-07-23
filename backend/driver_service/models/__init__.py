"""
Database models for the driver management microservice
"""
from .driver import Driver, Gender, LicenseType, EmploymentType, DriverStatus
from .driver_assignment import DriverAssignment, AssignmentStatus
from .driver_training import DriverTrainingRecord, TrainingType, TrainingStatus
from .driver_incident import DriverIncident, IncidentType, IncidentSeverity, IncidentStatus
from .driver_document import DriverDocument, DocumentType, DocumentStatus

__all__ = [
    "Driver", "Gender", "LicenseType", "EmploymentType", "DriverStatus",
    "DriverAssignment", "AssignmentStatus",
    "DriverTrainingRecord", "TrainingType", "TrainingStatus",
    "DriverIncident", "IncidentType", "IncidentSeverity", "IncidentStatus",
    "DriverDocument", "DocumentType", "DocumentStatus"
]