"""
Segment model for customer segmentation
"""
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json


class Segment(SQLModel, table=True):
    """Segment model for customer grouping and targeting"""
    __tablename__ = "segments"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Segment Information
    name: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Segmentation Criteria (stored as JSON)
    criteria: str = Field()  # JSON string containing segmentation rules
    
    # Metadata
    is_active: bool = Field(default=True, index=True)
    customer_count: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_calculated: Optional[datetime] = Field(default=None)
    
    def get_criteria_dict(self) -> Dict[str, Any]:
        """Parse criteria from JSON string"""
        try:
            return json.loads(self.criteria)
        except:
            return {}
    
    def set_criteria_dict(self, criteria_dict: Dict[str, Any]):
        """Set criteria as JSON string"""
        self.criteria = json.dumps(criteria_dict)
    
    def matches_customer(self, customer: "Customer") -> bool:
        """Check if a customer matches this segment's criteria"""
        criteria_dict = self.get_criteria_dict()
        
        # Example criteria matching logic
        if "loyalty_status" in criteria_dict:
            if customer.loyalty_status.value not in criteria_dict["loyalty_status"]:
                return False
        
        if "region" in criteria_dict:
            if customer.region not in criteria_dict["region"]:
                return False
        
        if "contact_type" in criteria_dict:
            if customer.contact_type.value not in criteria_dict["contact_type"]:
                return False
        
        if "tags" in criteria_dict:
            customer_tags = customer.get_tags_list()
            required_tags = criteria_dict["tags"]
            if not any(tag in customer_tags for tag in required_tags):
                return False
        
        return True