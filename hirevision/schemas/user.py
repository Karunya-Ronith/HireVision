"""
User-related Pydantic schemas for HireVision application
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic.networks import HttpUrl

from .base import BaseResponse, TimestampMixin, validate_phone_number, validate_url_optional


class UserRegistrationSchema(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=150, description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., min_length=1, max_length=30, description="First name")
    last_name: str = Field(..., min_length=1, max_length=30, description="Last name")
    password1: str = Field(..., min_length=8, description="Password")
    password2: str = Field(..., min_length=8, description="Password confirmation")
    phone: Optional[str] = Field(None, description="Phone number")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username"""
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        
        # Check for valid characters (letters, digits, @/./+/-/_)
        import re
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError("Username can only contain letters, digits and @/./+/-/_ characters")
        
        return v
    
    @field_validator('password2')
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match"""
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError("Passwords do not match")
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number"""
        return validate_phone_number(v)


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    username: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=1, description="Password")
    remember_me: bool = Field(False, description="Remember login")


class UserProfileSchema(BaseResponse, TimestampMixin):
    """Schema for user profile data"""
    id: UUID = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    bio: Optional[str] = Field(None, description="Biography")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    is_verified: bool = Field(False, description="Email verification status")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=30, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=30, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    bio: Optional[str] = Field(None, max_length=1000, description="Biography")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number"""
        return validate_phone_number(v)
    
    @field_validator('linkedin_url')
    @classmethod
    def validate_linkedin_url(cls, v: Optional[str]) -> Optional[HttpUrl]:
        """Validate LinkedIn URL"""
        return validate_url_optional(v)
    
    @field_validator('github_url')
    @classmethod
    def validate_github_url(cls, v: Optional[str]) -> Optional[HttpUrl]:
        """Validate GitHub URL"""
        return validate_url_optional(v)


class UserPasswordChangeSchema(BaseModel):
    """Schema for password change"""
    old_password: str = Field(..., min_length=1, description="Current password")
    new_password1: str = Field(..., min_length=8, description="New password")
    new_password2: str = Field(..., min_length=8, description="New password confirmation")
    
    @field_validator('new_password2')
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        """Validate that new passwords match"""
        if 'new_password1' in info.data and v != info.data['new_password1']:
            raise ValueError("New passwords do not match")
        return v


class UserPasswordResetSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address")


class UserPasswordResetConfirmSchema(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., min_length=1, description="Reset token")
    new_password1: str = Field(..., min_length=8, description="New password")
    new_password2: str = Field(..., min_length=8, description="New password confirmation")
    
    @field_validator('new_password2')
    @classmethod
    def validate_passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match"""
        if 'new_password1' in info.data and v != info.data['new_password1']:
            raise ValueError("Passwords do not match")
        return v 