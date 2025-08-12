from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Challenge(BaseModel):
    """Challenge model for coding challenges."""
    
    challenge_id = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    difficulty_id = Column(Integer, ForeignKey("difficulty.id"), nullable=False)
    points = Column(Integer, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="challenges")
    difficulty = relationship("Difficulty", back_populates="challenges")
    learning_objectives = relationship("LearningObjective", back_populates="challenge", cascade="all, delete-orphan")
    hints = relationship("Hint", back_populates="challenge", cascade="all, delete-orphan")
    challenge_tags = relationship("ChallengeTag", back_populates="challenge", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="challenge")
    
    def __repr__(self):
        return f"<Challenge {self.challenge_id}: {self.title}>"


class ChallengeTag(BaseModel):
    """Junction table for many-to-many relationship between Challenges and Tags."""
    
    challenge_id = Column(Integer, ForeignKey("challenge.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="challenge_tags")
    tag = relationship("Tag", back_populates="challenge_tags")
    
    def __repr__(self):
        return f"<ChallengeTag {self.challenge_id}:{self.tag_id}>"


class LearningObjective(BaseModel):
    """Learning objective model for challenge learning objectives."""
    
    challenge_id = Column(Integer, ForeignKey("challenge.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="learning_objectives")
    
    def __repr__(self):
        return f"<LearningObjective {self.id} for Challenge {self.challenge_id}>"


class Hint(BaseModel):
    """Hint model for challenge hints."""
    
    challenge_id = Column(Integer, ForeignKey("challenge.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="hints")
    
    def __repr__(self):
        return f"<Hint {self.id} for Challenge {self.challenge_id}>"