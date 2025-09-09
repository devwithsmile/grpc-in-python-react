"""
Pydantic schemas for borrowing validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from ..utils.validators import validate_positive_integer, ValidationError


class BorrowingCreateSchema(BaseModel):
    """Schema for creating a new borrowing record."""
    
    book_id: int = Field(..., gt=0, description="Book ID")
    member_id: int = Field(..., gt=0, description="Member ID")
    
    @validator('book_id')
    def validate_book_id(cls, v):
        """Validate book ID."""
        return validate_positive_integer(v, "Book ID")
    
    @validator('member_id')
    def validate_member_id(cls, v):
        """Validate member ID."""
        return validate_positive_integer(v, "Member ID")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "book_id": 1,
                "member_id": 1
            }
        }


class BorrowingReturnSchema(BaseModel):
    """Schema for returning a borrowed book."""
    
    book_id: int = Field(..., gt=0, description="Book ID")
    member_id: int = Field(..., gt=0, description="Member ID")
    
    @validator('book_id')
    def validate_book_id(cls, v):
        """Validate book ID."""
        return validate_positive_integer(v, "Book ID")
    
    @validator('member_id')
    def validate_member_id(cls, v):
        """Validate member ID."""
        return validate_positive_integer(v, "Member ID")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "book_id": 1,
                "member_id": 1
            }
        }


class BorrowingResponseSchema(BaseModel):
    """Schema for borrowing response data."""
    
    id: int = Field(..., description="Borrowing ID")
    book_id: int = Field(..., description="Book ID")
    member_id: int = Field(..., description="Member ID")
    borrow_date: Optional[str] = Field(None, description="Borrow date")
    return_date: Optional[str] = Field(None, description="Return date")
    is_returned: bool = Field(..., description="Whether the book has been returned")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "book_id": 1,
                "member_id": 1,
                "borrow_date": "2024-01-15T10:30:45Z",
                "return_date": None,
                "is_returned": False
            }
        }


class BorrowingIdSchema(BaseModel):
    """Schema for borrowing ID validation."""
    
    id: int = Field(..., gt=0, description="Borrowing ID")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate borrowing ID."""
        if not isinstance(v, int) or v <= 0:
            raise ValidationError(
                "Borrowing ID must be a positive integer",
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
