from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import BaseSchema


# Shared properties
class UserBase(BaseModel):
    """Base schema for user data."""
    
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_support: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for creating a user."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    """Schema for updating a user."""
    
    password: Optional[str] = Field(None, min_length=8)


# Properties to return via API
class User(BaseSchema, UserBase):
    """Schema for user response."""
    
    id: int
    username: str
    email: EmailStr
    is_support: bool


# Properties to return via API for user with posts
class UserWithPosts(User):
    """Schema for user response with posts."""
    
    posts: List[Any] = []  # Using Any to avoid circular import issues

