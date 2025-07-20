"""
Base Pydantic schemas and utilities for HireVision application
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseResponse(BaseModel):
    """Base response schema for all API responses"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True
    )


class ValidationError(BaseModel):
    """Validation error schema"""
    field: str
    message: str
    value: Optional[Any] = None


class PaginationSchema(BaseModel):
    """Pagination schema for list responses"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    total_items: int = Field(default=0, ge=0, description="Total number of items")
    total_pages: int = Field(default=0, ge=0, description="Total number of pages")


class FileSchema(BaseModel):
    """Base file schema for file uploads"""
    filename: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., gt=0, le=10_485_760, description="File size in bytes (max 10MB)")
    content_type: str


class UUIDSchema(BaseModel):
    """UUID validation schema"""
    id: UUID = Field(..., description="UUID identifier")


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class UserBaseMixin(BaseModel):
    """Base mixin for user-related schemas"""
    user_id: Optional[UUID] = Field(None, description="Associated user ID")


# Common field validators
def validate_non_empty_string(v: str, field_name: str = "Field") -> str:
    """Validate that a string is not empty after stripping whitespace"""
    if not v or not v.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return v.strip()


def validate_phone_number(v: Optional[str]) -> Optional[str]:
    """Validate phone number format"""
    if not v:
        return v
    
    # Basic phone number validation (adjust regex as needed)
    import re
    phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
    if not re.match(phone_pattern, v.strip()):
        raise ValueError("Invalid phone number format")
    
    return v.strip()


def validate_url_optional(v: Optional[str]) -> Optional[str]:
    """Validate optional URL"""
    if not v or not v.strip():
        return None
    
    # Add protocol if missing
    url = v.strip()
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    return url


class JSONFieldSchema(BaseModel):
    """Schema for validating JSON fields"""
    data: Union[Dict[str, Any], List[Any]] = Field(default_factory=dict, description="JSON data") 