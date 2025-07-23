"""
Template model for notification templates
"""
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.notification import NotificationChannel
import uuid
import json


class TemplateType(str, Enum):
    """Template type enumeration"""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    SYSTEM = "system"
    ALERT = "alert"


class Template(SQLModel, table=True):
    """Template model for notification templates"""
    __tablename__ = "templates"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Template Identification
    name: str = Field(unique=True, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    type: TemplateType = Field(index=True)
    
    # Channel and Content
    channel: NotificationChannel = Field(index=True)
    subject: Optional[str] = Field(default=None, max_length=500)  # For email
    body: str = Field(max_length=10000)
    
    # Template Configuration
    variables: Optional[str] = Field(default=None)  # JSON schema for variables
    default_values: Optional[str] = Field(default=None)  # JSON for default variable values
    
    # Formatting
    content_type: str = Field(default="text", max_length=20)  # text, html, markdown
    language: str = Field(default="en", max_length=5)
    
    # Status and Metadata
    is_active: bool = Field(default=True, index=True)
    version: int = Field(default=1, ge=1)
    
    # Usage Tracking
    usage_count: int = Field(default=0, ge=0)
    last_used_at: Optional[datetime] = Field(default=None)
    
    # Validation
    is_validated: bool = Field(default=False)
    validation_errors: Optional[str] = Field(default=None, max_length=1000)
    
    # Audit Fields
    created_by: Optional[uuid.UUID] = Field(default=None)
    updated_by: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_variables_schema(self) -> Dict[str, Any]:
        """Parse variables schema from JSON string"""
        if not self.variables:
            return {}
        try:
            return json.loads(self.variables)
        except:
            return {}
    
    def set_variables_schema(self, schema: Dict[str, Any]):
        """Set variables schema as JSON string"""
        self.variables = json.dumps(schema) if schema else None
    
    def get_default_values_dict(self) -> Dict[str, Any]:
        """Parse default values from JSON string"""
        if not self.default_values:
            return {}
        try:
            return json.loads(self.default_values)
        except:
            return {}
    
    def set_default_values_dict(self, defaults: Dict[str, Any]):
        """Set default values as JSON string"""
        self.default_values = json.dumps(defaults) if defaults else None
    
    def render(self, variables: Dict[str, Any] = None) -> Dict[str, str]:
        """Render template with variables"""
        if variables is None:
            variables = {}
        
        # Merge with default values
        defaults = self.get_default_values_dict()
        merged_vars = {**defaults, **variables}
        
        # Simple template rendering (in production, use Jinja2 or similar)
        rendered_subject = self.subject
        rendered_body = self.body
        
        if rendered_subject:
            for key, value in merged_vars.items():
                rendered_subject = rendered_subject.replace(f"{{{key}}}", str(value))
        
        for key, value in merged_vars.items():
            rendered_body = rendered_body.replace(f"{{{key}}}", str(value))
        
        return {
            "subject": rendered_subject,
            "body": rendered_body
        }
    
    def validate_variables(self, variables: Dict[str, Any]) -> List[str]:
        """Validate provided variables against schema"""
        errors = []
        schema = self.get_variables_schema()
        
        # Check required variables
        required_vars = [k for k, v in schema.items() if v.get("required", False)]
        for var in required_vars:
            if var not in variables:
                errors.append(f"Required variable '{var}' is missing")
        
        # Check variable types (basic validation)
        for var, value in variables.items():
            if var in schema:
                expected_type = schema[var].get("type")
                if expected_type and not isinstance(value, type(expected_type)):
                    errors.append(f"Variable '{var}' should be of type {expected_type}")
        
        return errors
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()