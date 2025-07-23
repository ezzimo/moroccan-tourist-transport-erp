"""
Tests for tour template functionality
"""
import pytest
from services.tour_template_service import TourTemplateService
from schemas.tour_template import TourTemplateCreate
from models.tour_template import TourCategory, DifficultyLevel


class TestTourTemplates:
    """Test class for tour template operations"""
    
    @pytest.mark.asyncio
    async def test_create_tour_template(self, session, sample_tour_template_data):
        """Test creating a new tour template"""
        template_service = TourTemplateService(session)
        
        template_create = TourTemplateCreate(**sample_tour_template_data)
        template = await template_service.create_template(template_create)
        
        assert template.title == sample_tour_template_data["title"]
        assert template.category == TourCategory.DESERT
        assert template.duration_days == 3
        assert template.difficulty_level == DifficultyLevel.MODERATE
        assert template.is_active is True
        assert len(template.highlights) == 3
        assert "Camel trekking" in template.highlights
    
    @pytest.mark.asyncio
    async def test_create_template_duplicate_title(self, session, sample_tour_template_data):
        """Test creating template with duplicate title"""
        template_service = TourTemplateService(session)
        
        template_create = TourTemplateCreate(**sample_tour_template_data)
        
        # Create first template
        await template_service.create_template(template_create)
        
        # Try to create second template with same title
        with pytest.raises(Exception) as exc_info:
            await template_service.create_template(template_create)
        
        assert "already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_tour_template(self, session, create_test_tour_template):
        """Test getting tour template by ID"""
        template_service = TourTemplateService(session)
        
        # Create test template
        test_template = create_test_tour_template(
            title="Desert Adventure",
            category=TourCategory.DESERT
        )
        
        # Get template
        retrieved_template = await template_service.get_template(test_template.id)
        
        assert retrieved_template.id == test_template.id
        assert retrieved_template.title == "Desert Adventure"
        assert retrieved_template.category == TourCategory.DESERT
    
    @pytest.mark.asyncio
    async def test_update_tour_template(self, session, create_test_tour_template):
        """Test updating tour template information"""
        from schemas.tour_template import TourTemplateUpdate
        
        template_service = TourTemplateService(session)
        
        # Create test template
        test_template = create_test_tour_template()
        
        # Update template
        update_data = TourTemplateUpdate(
            title="Updated Desert Tour",
            duration_days=5,
            highlights=["Updated highlight 1", "Updated highlight 2"],
            is_featured=True
        )
        
        updated_template = await template_service.update_template(
            test_template.id, update_data
        )
        
        assert updated_template.title == "Updated Desert Tour"
        assert updated_template.duration_days == 5
        assert updated_template.is_featured is True
        assert len(updated_template.highlights) == 2
        assert updated_template.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_duplicate_template(self, session, create_test_tour_template):
        """Test duplicating a tour template"""
        template_service = TourTemplateService(session)
        
        # Create original template
        original_template = create_test_tour_template(
            title="Original Tour",
            description="Original description"
        )
        original_template.set_highlights_list(["Highlight 1", "Highlight 2"])
        session.add(original_template)
        session.commit()
        
        # Duplicate template
        duplicated_template = await template_service.duplicate_template(
            original_template.id, "Duplicated Tour"
        )
        
        assert duplicated_template.title == "Duplicated Tour"
        assert duplicated_template.description == original_template.description
        assert duplicated_template.category == original_template.category
        assert duplicated_template.duration_days == original_template.duration_days
        assert duplicated_template.highlights == original_template.get_highlights_list()
        assert duplicated_template.is_featured is False  # Should not be featured by default
    
    @pytest.mark.asyncio
    async def test_get_featured_templates(self, session, create_test_tour_template):
        """Test getting featured tour templates"""
        template_service = TourTemplateService(session)
        
        # Create templates
        featured_template = create_test_tour_template(
            title="Featured Tour",
            is_featured=True
        )
        regular_template = create_test_tour_template(
            title="Regular Tour",
            is_featured=False
        )
        
        # Get featured templates
        featured_templates = await template_service.get_featured_templates(limit=10)
        
        assert len(featured_templates) == 1
        assert featured_templates[0].id == featured_template.id
        assert featured_templates[0].is_featured is True
    
    @pytest.mark.asyncio
    async def test_get_templates_by_category(self, session, create_test_tour_template):
        """Test getting templates by category"""
        template_service = TourTemplateService(session)
        
        # Create templates in different categories
        desert_template = create_test_tour_template(
            title="Desert Tour",
            category=TourCategory.DESERT
        )
        cultural_template = create_test_tour_template(
            title="Cultural Tour",
            category=TourCategory.CULTURAL
        )
        
        # Get desert templates
        desert_templates = await template_service.get_templates_by_category(
            TourCategory.DESERT.value, limit=20
        )
        
        assert len(desert_templates) == 1
        assert desert_templates[0].id == desert_template.id
        assert desert_templates[0].category == TourCategory.DESERT
    
    @pytest.mark.asyncio
    async def test_search_templates(self, session, create_test_tour_template):
        """Test searching tour templates"""
        from schemas.tour_template import TourTemplateSearch
        from utils.pagination import PaginationParams
        
        template_service = TourTemplateService(session)
        
        # Create test templates
        create_test_tour_template(
            title="Sahara Desert Adventure",
            category=TourCategory.DESERT,
            duration_days=3,
            default_region="Merzouga"
        )
        create_test_tour_template(
            title="Atlas Mountains Trek",
            category=TourCategory.ADVENTURE,
            duration_days=5,
            default_region="Atlas"
        )
        
        # Search by query
        search = TourTemplateSearch(query="Sahara")
        pagination = PaginationParams(page=1, size=10)
        
        templates, total = await template_service.get_templates(pagination, search)
        
        assert total == 1
        assert "Sahara" in templates[0].title
        
        # Search by category
        search = TourTemplateSearch(category=TourCategory.ADVENTURE)
        templates, total = await template_service.get_templates(pagination, search)
        
        assert total == 1
        assert templates[0].category == TourCategory.ADVENTURE
        
        # Search by duration range
        search = TourTemplateSearch(min_duration=4, max_duration=6)
        templates, total = await template_service.get_templates(pagination, search)
        
        assert total == 1
        assert templates[0].duration_days == 5
    
    @pytest.mark.asyncio
    async def test_delete_template_with_instances(self, session, create_test_tour_template, create_test_tour_instance):
        """Test deleting template that has associated tour instances"""
        template_service = TourTemplateService(session)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Try to delete template
        result = await template_service.delete_template(test_template.id)
        
        assert "deactivated" in result["message"]
        
        # Verify template is deactivated, not deleted
        deactivated_template = await template_service.get_template(test_template.id)
        assert deactivated_template.is_active is False
    
    @pytest.mark.asyncio
    async def test_delete_template_without_instances(self, session, create_test_tour_template):
        """Test deleting template that has no associated tour instances"""
        template_service = TourTemplateService(session)
        
        # Create template without instances
        test_template = create_test_tour_template()
        
        # Delete template
        result = await template_service.delete_template(test_template.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify template is deleted
        with pytest.raises(Exception) as exc_info:
            await template_service.get_template(test_template.id)
        
        assert "not found" in str(exc_info.value)