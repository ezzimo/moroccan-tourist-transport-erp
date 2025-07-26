"""
Pydantic schemas for request/response models
"""
from .driver import (
    DriverCreate, DriverUpdate, DriverResponse, DriverSummary,
    DriverSearch, DriverPerformance, DriverAvailability, DriverComplianceStatus
)
from .driver_assignment import (
    DriverAssignmentCreate, DriverAssignmentUpdate, DriverAssignmentResponse,
    AssignmentSummary, AssignmentConflict
)
from .driver_training import (
    DriverTrainingCreate, DriverTrainingUpdate, DriverTrainingResponse,
    TrainingSummary, TrainingComplianceReport
)
from .driver_incident import (
    DriverIncidentCreate, DriverIncidentUpdate, DriverIncidentResponse,
    IncidentSummary, IncidentTrend
)
from .driver_document import (
    DriverDocumentCreate, DriverDocumentUpdate, DriverDocumentResponse,
    DocumentSummary
)
from .mobile import (
    DriverDashboard, AssignmentDetails, OfflineDataBundle,
    StatusUpdate, IncidentReport, NotificationItem, PerformanceMetrics
)

__all__ = [
    # Driver schemas
    "DriverCreate", "DriverUpdate", "DriverResponse", "DriverSummary",
    "DriverSearch", "DriverPerformance", "DriverAvailability", "DriverComplianceStatus",
    
    # Assignment schemas
    "DriverAssignmentCreate", "DriverAssignmentUpdate", "DriverAssignmentResponse",
    "AssignmentSummary", "AssignmentConflict",
    
    # Training schemas
    "DriverTrainingCreate", "DriverTrainingUpdate", "DriverTrainingResponse",
    "TrainingSummary", "TrainingComplianceReport",
    
    # Incident schemas
    "DriverIncidentCreate", "DriverIncidentUpdate", "DriverIncidentResponse",
    "IncidentSummary", "IncidentTrend",
    
    # Document schemas
    "DriverDocumentCreate", "DriverDocumentUpdate", "DriverDocumentResponse",
    "DocumentSummary",
    
    # Mobile schemas
    "DriverDashboard", "AssignmentDetails", "OfflineDataBundle",
    "StatusUpdate", "IncidentReport", "NotificationItem", "PerformanceMetrics"
]