"""
Tour template model for reusable tour definitions
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class TourCategory(str, Enum):
    """Tour category enumeration"""
    CULTURAL = "Cultural"
    ADVENTURE = "Adventure"
    DESERT = "Desert"
    COASTAL = "Coastal"
    CITY = "City"
    CUSTOM = "Custom"


class DifficultyLevel(str, Enum):
    """Tour difficulty level enumeration"""
    EASY = "Easy"
    MODERATE = "Moderate"
    CHALLENGING = "Challenging"
    EXPERT = "Expert"


class TourTemplate(SQLModel, table=True):
    """Tour template model for reusable tour definitions"""
    __tablename__ = "tour_templates"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic Information
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    short_description: Optional[str] = Field(default=None, max_length=500)
    
    # Tour Details
    category: TourCategory = Field(index=True)
    duration_days: int = Field(ge=1, le=30)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.EASY)
    
    # Location & Language
    default_language: str = Field(default="French", max_length=50)
    default_region: str = Field(max_length=100, index=True)
    starting_location: Optional[str] = Field(default=None, max_length=255)
    ending_location: Optional[str] = Field(default=None, max_length=255)
    
    # Capacity & Pricing
    min_participants: int = Field(default=1, ge=1)
    max_participants: int = Field(default=20, ge=1)
    base_price: Optional[float] = Field(default=None, ge=0)
    
    # Content
    highlights: Optional[str] = Field(default=None)  # JSON string of highlights
    inclusions: Optional[str] = Field(default=None)  # JSON string of inclusions
    exclusions: Optional[str] = Field(default=None)  # JSON string of exclusions
    requirements: Optional[str] = Field(default=None, max_length=1000)
    
    # Status & Metadata
    is_active: bool = Field(default=True, index=True)
    is_featured: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    tour_instances: List["TourInstance"] = Relationship(back_populates="template")
    
    def get_highlights_list(self) -> List[str]:
        """Parse highlights from JSON string"""
        if not self.highlights:
            return []
        try:
            import json
            return json.loads(self.highlights)
        except:
            return []
    
    def set_highlights_list(self, highlights: List[str]):
        """Set highlights as JSON string"""
        import json
        self.highlights = json.dumps(highlights) if highlights else None
    
    def get_inclusions_list(self) -> List[str]:
        """Parse inclusions from JSON string"""
        if not self.inclusions:
            return []
        try:
            import json
            return json.loads(self.inclusions)
        except:
            return []
    
    def set_inclusions_list(self, inclusions: List[str]):
        """Set inclusions as JSON string"""
        import json
        self.inclusions = json.dumps(inclusions) if inclusions else None
    
    def get_exclusions_list(self) -> List[str]:
        """Parse exclusions from JSON string"""
        if not self.exclusions:
            return []
        try:
            import json
            return json.loads(self.exclusions)
        except:
            return []
    
    def set_exclusions_list(self, exclusions: List[str]):
        """Set exclusions as JSON string"""
        import json
        self.exclusions = json.dumps(exclusions) if exclusions else None