"""
Pydantic schemas for book validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from ..utils.validators import validate_isbn, validate_required_string, ValidationError


class BookCreateSchema(BaseModel):
    """Schema for creating a new book."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Book author")
    isbn: Optional[str] = Field(None, max_length=17, description="ISBN-10 or ISBN-13")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate book title."""
        return validate_required_string(v, "Title", min_length=1, max_length=255)
    
    @validator('author')
    def validate_author(cls, v):
        """Validate book author."""
        return validate_required_string(v, "Author", min_length=1, max_length=255)
    
    @validator('isbn')
    def validate_isbn(cls, v):
        """Validate ISBN format."""
        if v is None or v.strip() == "":
            return None
        return validate_isbn(v.strip())
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Add any custom encoders if needed
        }
        schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0743273565"
            }
        }


class BookUpdateSchema(BaseModel):
    """Schema for updating an existing book."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Book title")
    author: Optional[str] = Field(None, min_length=1, max_length=255, description="Book author")
    isbn: Optional[str] = Field(None, max_length=17, description="ISBN-10 or ISBN-13")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate book title."""
        if v is None:
            return v
        return validate_required_string(v, "Title", min_length=1, max_length=255)
    
    @validator('author')
    def validate_author(cls, v):
        """Validate book author."""
        if v is None:
            return v
        return validate_required_string(v, "Author", min_length=1, max_length=255)
    
    @validator('isbn')
    def validate_isbn(cls, v):
        """Validate ISBN format."""
        if v is None or v.strip() == "":
            return None
        return validate_isbn(v.strip())
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "title": "The Great Gatsby (Updated)",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0743273565"
            }
        }


class BookResponseSchema(BaseModel):
    """Schema for book response data."""
    
    id: int = Field(..., description="Book ID")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    isbn: Optional[str] = Field(None, description="ISBN-10 or ISBN-13")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0743273565",
                "created_at": "2024-01-15T10:30:45Z",
                "updated_at": "2024-01-15T10:30:45Z"
            }
        }


class BookIdSchema(BaseModel):
    """Schema for book ID validation."""
    
    id: int = Field(..., gt=0, description="Book ID")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate book ID."""
        if not isinstance(v, int) or v <= 0:
            raise ValidationError(
                "Book ID must be a positive integer",
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
