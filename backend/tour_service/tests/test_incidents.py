"""
Tests for incident functionality
"""
import pytest
from services.incident_service import IncidentService
from schemas.incident import IncidentCreate, IncidentResolution, IncidentEscalation
from models.incident import IncidentType, SeverityLevel
import uuid


class TestIncidents:
    """Test class for incident operations"""
    
    @pytest.mark.asyncio
    async def test_create_incident(self, session, redis_client, create_test_tour_template, create_test_tour_instance, sample_incident_data):
        """Test creating a new incident"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create incident
        incident_data = IncidentCreate(
            tour_instance_id=test_instance.id,
            reporter_id=uuid.uuid4(),
            **sample_incident_data
        )
        
        incident = await incident_service.create_incident(incident_data)
        
        assert incident.tour_instance_id == test_instance.id
        assert incident.incident_type == IncidentType.DELAY
        assert incident.severity == SeverityLevel.MEDIUM
        assert incident.title == "Traffic delay on route"
        assert incident.affected_participants == 4
        assert incident.estimated_delay_minutes == 30
        assert incident.is_resolved is False
        assert incident.priority_score > 0
    
    @pytest.mark.asyncio
    async def test_incident_priority_calculation(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test incident priority score calculation"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create high severity medical incident
        medical_incident = IncidentCreate(
            tour_instance_id=test_instance.id,
            reporter_id=uuid.uuid4(),
            incident_type=IncidentType.MEDICAL,
            severity=SeverityLevel.HIGH,
            title="Medical emergency",
            description="Tourist injured during hike"
        )
        
        medical_result = await incident_service.create_incident(medical_incident)
        
        # Create low severity delay incident
        delay_incident = IncidentCreate(
            tour_instance_id=test_instance.id,
            reporter_id=uuid.uuid4(),
            incident_type=IncidentType.DELAY,
            severity=SeverityLevel.LOW,
            title="Minor delay",
            description="5-minute delay due to traffic"
        )
        
        delay_result = await incident_service.create_incident(delay_incident)
        
        # Medical incident should have higher priority
        assert medical_result.priority_score > delay_result.priority_score
        assert medical_result.is_urgent is True
        assert delay_result.is_urgent is False
    
    @pytest.mark.asyncio
    async def test_resolve_incident(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test resolving an incident"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create unresolved incident
        test_incident = create_test_incident(
            test_instance.id,
            title="Vehicle breakdown",
            is_resolved=False
        )
        
        # Resolve incident
        resolution_data = IncidentResolution(
            resolution_description="Replacement vehicle arranged",
            resolved_by=uuid.uuid4(),
            requires_follow_up=True,
            follow_up_notes="Check vehicle maintenance schedule"
        )
        
        resolved_incident = await incident_service.resolve_incident(
            test_incident.id, resolution_data
        )
        
        assert resolved_incident.is_resolved is True
        assert resolved_incident.resolution_description == "Replacement vehicle arranged"
        assert resolved_incident.resolved_by == resolution_data.resolved_by
        assert resolved_incident.resolved_at is not None
        assert resolved_incident.requires_follow_up is True
        assert resolved_incident.follow_up_notes == "Check vehicle maintenance schedule"
    
    @pytest.mark.asyncio
    async def test_escalate_incident(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test escalating an incident"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create unresolved incident
        test_incident = create_test_incident(
            test_instance.id,
            title="Customer complaint",
            severity=SeverityLevel.HIGH,
            is_resolved=False
        )
        
        # Escalate incident
        escalation_data = IncidentEscalation(
            escalated_to=uuid.uuid4(),
            escalation_reason="Requires management attention",
            notes="Customer threatening legal action"
        )
        
        escalated_incident = await incident_service.escalate_incident(
            test_incident.id, escalation_data
        )
        
        assert escalated_incident.escalated_to == escalation_data.escalated_to
        assert "Escalated to" in escalated_incident.follow_up_notes
        assert "Requires management attention" in escalated_incident.follow_up_notes
        assert escalated_incident.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_cannot_escalate_resolved_incident(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test that resolved incidents cannot be escalated"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create resolved incident
        test_incident = create_test_incident(
            test_instance.id,
            is_resolved=True
        )
        
        # Try to escalate resolved incident
        escalation_data = IncidentEscalation(
            escalated_to=uuid.uuid4(),
            escalation_reason="Should not work"
        )
        
        with pytest.raises(Exception) as exc_info:
            await incident_service.escalate_incident(test_incident.id, escalation_data)
        
        assert "Cannot escalate resolved incident" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_urgent_incidents(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test getting urgent unresolved incidents"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create various incidents
        urgent_medical = create_test_incident(
            test_instance.id,
            title="Medical Emergency",
            incident_type=IncidentType.MEDICAL,
            severity=SeverityLevel.HIGH,
            is_resolved=False
        )
        
        urgent_safety = create_test_incident(
            test_instance.id,
            title="Safety Issue",
            incident_type=IncidentType.SAFETY,
            severity=SeverityLevel.MEDIUM,
            is_resolved=False
        )
        
        resolved_critical = create_test_incident(
            test_instance.id,
            title="Resolved Critical",
            severity=SeverityLevel.CRITICAL,
            is_resolved=True
        )
        
        minor_delay = create_test_incident(
            test_instance.id,
            title="Minor Delay",
            incident_type=IncidentType.DELAY,
            severity=SeverityLevel.LOW,
            is_resolved=False
        )
        
        # Get urgent incidents
        urgent_incidents = await incident_service.get_urgent_incidents()
        
        # Should include medical and safety incidents, but not resolved or minor ones
        urgent_titles = [incident.title for incident in urgent_incidents]
        assert "Medical Emergency" in urgent_titles
        assert "Safety Issue" in urgent_titles
        assert "Resolved Critical" not in urgent_titles
        assert "Minor Delay" not in urgent_titles
    
    @pytest.mark.asyncio
    async def test_get_incident_stats(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test getting incident statistics"""
        incident_service = IncidentService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create various incidents
        create_test_incident(
            test_instance.id,
            incident_type=IncidentType.DELAY,
            severity=SeverityLevel.LOW,
            is_resolved=True
        )
        create_test_incident(
            test_instance.id,
            incident_type=IncidentType.MEDICAL,
            severity=SeverityLevel.HIGH,
            is_resolved=False
        )
        create_test_incident(
            test_instance.id,
            incident_type=IncidentType.DELAY,
            severity=SeverityLevel.MEDIUM,
            is_resolved=True
        )
        
        # Get statistics
        stats = await incident_service.get_incident_stats(days=30)
        
        assert stats.total_incidents == 3
        assert stats.resolved_incidents == 2
        assert stats.unresolved_incidents == 1
        assert stats.by_type["Delay"] == 2
        assert stats.by_type["Medical"] == 1
        assert stats.by_severity["Low"] == 1
        assert stats.by_severity["Medium"] == 1
        assert stats.by_severity["High"] == 1
        assert stats.urgent_incidents == 1  # Medical incident
    
    @pytest.mark.asyncio
    async def test_get_tour_incidents(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_incident):
        """Test getting all incidents for a specific tour"""
        from utils.pagination import PaginationParams
        
        incident_service = IncidentService(session, redis_client)
        
        # Create templates and instances
        test_template = create_test_tour_template()
        test_instance1 = create_test_tour_instance(test_template.id)
        test_instance2 = create_test_tour_instance(test_template.id)
        
        # Create incidents for different tours
        create_test_incident(test_instance1.id, title="Tour 1 Incident 1")
        create_test_incident(test_instance1.id, title="Tour 1 Incident 2")
        create_test_incident(test_instance2.id, title="Tour 2 Incident 1")
        
        # Get incidents for tour 1
        pagination = PaginationParams(page=1, size=10)
        incidents, total = await incident_service.get_tour_incidents(test_instance1.id, pagination)
        
        assert total == 2
        assert len(incidents) == 2
        incident_titles = [incident.title for incident in incidents]
        assert "Tour 1 Incident 1" in incident_titles
        assert "Tour 1 Incident 2" in incident_titles
        assert "Tour 2 Incident 1" not in incident_titles