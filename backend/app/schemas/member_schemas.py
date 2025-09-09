"""
Pydantic schemas for member validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from ..utils.validators import validate_email_address, validate_phone, validate_required_string, ValidationError


class MemberCreateSchema(BaseModel):
    """Schema for creating a new member."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Member name")
    email: str = Field(..., max_length=255, description="Member email address")
    phone: Optional[str] = Field(None, max_length=20, description="Member phone number")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate member name."""
        return validate_required_string(v, "Name", min_length=1, max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email address."""
        return validate_email_address(v)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        if v is None or v.strip() == "":
            return None
        return validate_phone(v.strip())
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567"
            }
        }


class MemberUpdateSchema(BaseModel):
    """Schema for updating an existing member."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Member name")
    email: Optional[str] = Field(None, max_length=255, description="Member email address")
    phone: Optional[str] = Field(None, max_length=20, description="Member phone number")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate member name."""
        if v is None:
            return v
        return validate_required_string(v, "Name", min_length=1, max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email address."""
        if v is None:
            return v
        return validate_email_address(v)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        if v is None or v.strip() == "":
            return None
        return validate_phone(v.strip())
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "name": "John Doe (Updated)",
                "email": "john.doe.updated@example.com",
                "phone": "+1-555-987-6543"
            }
        }


class MemberResponseSchema(BaseModel):
    """Schema for member response data."""
    
    id: int = Field(..., description="Member ID")
    name: str = Field(..., description="Member name")
    email: str = Field(..., description="Member email address")
    phone: Optional[str] = Field(None, description="Member phone number")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "created_at": "2024-01-15T10:30:45Z",
                "updated_at": "2024-01-15T10:30:45Z"
            }
        }


class MemberIdSchema(BaseModel):
    """Schema for member ID validation."""
    
    id: int = Field(..., gt=0, description="Member ID")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate member ID."""
        if not isinstance(v, int) or v <= 0:
            raise ValidationError(
                "Member ID must be a positive integer",
                field="id",
                value=v
            )
        return v
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "id": 1
            }
        }
