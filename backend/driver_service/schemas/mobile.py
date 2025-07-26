"""
Mobile API-specific Pydantic schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from models.driver_assignment import AssignmentStatus
from models.driver_incident import IncidentType, IncidentSeverity
from schemas.driver_assignment import DriverAssignmentResponse
from schemas.driver import DriverResponse
import uuid


class DriverDashboard(BaseModel):
    """Driver dashboard data for mobile app"""
    driver: DriverResponse
    today_assignments: List[DriverAssignmentResponse]
    upcoming_assignments: List[DriverAssignmentResponse]
    unread_notifications: int
    performance_score: float
    total_tours_completed: int
    license_expiry_days: int
    health_cert_expiry_days: Optional[int]
    alerts: List[str]


class AssignmentDetails(BaseModel):
    """Detailed assignment information with itinerary"""
    assignment: DriverAssignmentResponse
    itinerary: List[Dict[str, Any]]
    vehicle_info: Optional[Dict[str, Any]]
    customer_info: Optional[Dict[str, Any]]
    emergency_contacts: List[Dict[str, str]]
    special_requirements: List[str]


class StatusUpdate(BaseModel):
    """Status update from mobile app"""
    status: AssignmentStatus
    notes: Optional[str] = None
    location: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class IncidentReport(BaseModel):
    """Incident report from mobile app"""
    assignment_id: Optional[uuid.UUID] = None
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    location: Optional[str] = None
    photos_taken: bool = False
    customer_involved: bool = False
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    witness_names: Optional[str] = None


class OfflineDataBundle(BaseModel):
    """Offline data bundle for mobile app"""
    driver_profile: DriverResponse
    assignments: List[DriverAssignmentResponse]
    documents: List[Dict[str, Any]]
    training_records: List[Dict[str, Any]]
    emergency_contacts: List[Dict[str, str]]
    company_policies: List[Dict[str, str]]
    last_sync: datetime
    expires_at: datetime


class NotificationItem(BaseModel):
    """Notification item for mobile"""
    id: uuid.UUID
    title: str
    message: str
    type: str
    priority: str
    is_read: bool
    created_at: datetime
    action_url: Optional[str] = None


class PerformanceMetrics(BaseModel):
    """Driver performance metrics for mobile"""
    overall_score: float
    total_assignments: int
    completed_assignments: int
    completion_rate: float
    average_rating: Optional[float]
    on_time_rate: float
    incident_count: int
    last_training_date: Optional[date]
    certificates_expiring: int
    monthly_trends: List[Dict[str, Any]]