from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for both regular users and support team members."""
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    is_support = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Category(BaseModel):
    """Category model for categorizing challenges and conversations."""
    
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    challenges = relationship("Challenge", back_populates="category")
    conversations = relationship("Conversation", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Difficulty(BaseModel):
    """Difficulty model for challenge difficulty levels."""
    
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relationships
    challenges = relationship("Challenge", back_populates="difficulty")
    
    def __repr__(self):
        return f"<Difficulty {self.name}>"


class Tag(BaseModel):
    """Tag model for tagging challenges."""
    
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relationships
    challenge_tags = relationship("ChallengeTag", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag {self.name}>"