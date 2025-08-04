from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


# Tag schemas
class TagBase(BaseModel):
    """Base schema for tag data."""
    
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class Tag(BaseSchema, TagBase):
    """Schema for tag response."""
    
    id: int


# Learning Objective schemas
class LearningObjectiveBase(BaseModel):
    """Base schema for learning objective data."""
    
    description: str = Field(..., min_length=5)


class LearningObjectiveCreate(LearningObjectiveBase):
    """Schema for creating a learning objective."""
    pass


class LearningObjective(BaseSchema, LearningObjectiveBase):
    """Schema for learning objective response."""
    
    id: int
    challenge_id: int


# Hint schemas
class HintBase(BaseModel):
    """Base schema for hint data."""
    
    description: str = Field(..., min_length=5)


class HintCreate(HintBase):
    """Schema for creating a hint."""
    pass


class Hint(BaseSchema, HintBase):
    """Schema for hint response."""
    
    id: int
    challenge_id: int


# Category schemas
class CategoryBase(BaseModel):
    """Base schema for category data."""
    
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class Category(BaseSchema, CategoryBase):
    """Schema for category response."""
    
    id: int


# Difficulty schemas
class DifficultyBase(BaseModel):
    """Base schema for difficulty data."""
    
    name: str = Field(..., min_length=1, max_length=50)


class DifficultyCreate(DifficultyBase):
    """Schema for creating a difficulty."""
    pass


class Difficulty(BaseSchema, DifficultyBase):
    """Schema for difficulty response."""
    
    id: int


# Challenge schemas
class ChallengeBase(BaseModel):
    """Base schema for challenge data."""
    
    challenge_id: str = Field(..., min_length=5, max_length=20, pattern=r"^CHAL_\d+$")
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    category_id: Optional[int] = None
    difficulty_id: Optional[int] = None
    points: int = Field(..., ge=0)


class ChallengeCreate(ChallengeBase):
    """Schema for creating a challenge."""
    
    category_id: int
    difficulty_id: int
    tags: List[str] = []
    learning_objectives: List[str] = []
    hints: List[str] = []
    
    @validator("points")
    def points_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Points must be a positive integer")
        return v


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge."""
    
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    category_id: Optional[int] = None
    difficulty_id: Optional[int] = None
    points: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    hints: Optional[List[str]] = None


class Challenge(BaseSchema, ChallengeBase):
    """Schema for challenge response."""
    
    id: int
    category: Category
    difficulty: Difficulty
    tags: List[Tag] = []
    learning_objectives: List[LearningObjective] = []
    hints: List[Hint] = []


# For challenge search and filtering
class ChallengeFilter(BaseModel):
    """Schema for challenge filtering."""
    
    category_id: Optional[int] = None
    difficulty_id: Optional[int] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    min_points: Optional[int] = Field(None, ge=0)
    max_points: Optional[int] = Field(None, ge=0)