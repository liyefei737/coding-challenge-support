from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.schemas.base import BaseSchema
from app.schemas.user import User


# Post schemas
class PostBase(BaseModel):
    """Base schema for post data."""
    
    content: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None


class PostCreate(PostBase):
    """Schema for creating a post."""
    
    user_id: Optional[int] = None  # Will be set from the current user if not provided


class Post(BaseSchema, PostBase):
    """Schema for post response."""
    
    id: int
    post_id: int
    conversation_id: int
    user_id: int
    user: Optional[User] = None


# Conversation schemas
class ConversationBase(BaseModel):
    """Base schema for conversation data."""
    
    identifier: Optional[str] = Field(None, min_length=5, max_length=20, pattern=r"^CONV_\d+$")
    topic: str = Field(..., min_length=3, max_length=200)
    category_id: Optional[int] = None
    challenge_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    
    category_id: int
    challenge_id: str
    initial_post: str = Field(..., min_length=1)
    
    @field_validator("topic")
    @classmethod
    def topic_must_be_descriptive(cls, v):
        if len(v.split()) < 2:
            raise ValueError("Topic must be descriptive (at least 2 words)")
        return v


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    
    topic: Optional[str] = Field(None, min_length=3, max_length=200)
    category_id: Optional[int] = None
    challenge_id: Optional[int] = None


class Conversation(BaseSchema, ConversationBase):
    """Schema for conversation response."""
    
    id: int
    identifier: str
    posts: List[Post] = []


# For conversation search and filtering
class ConversationFilter(BaseModel):
    """Schema for conversation filtering."""
    
    category_id: Optional[int] = None
    challenge_id: Optional[int] = None
    search: Optional[str] = None
    user_id: Optional[int] = None