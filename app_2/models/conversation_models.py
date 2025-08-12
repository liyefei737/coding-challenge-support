from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Conversation(BaseModel):
    """Conversation model for support conversations."""
    
    identifier = Column(String(20), unique=True, index=True, nullable=False)
    topic = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenge.id"), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="conversations")
    challenge = relationship("Challenge", back_populates="conversations")
    posts = relationship("Post", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.identifier}: {self.topic}>"


class Post(BaseModel):
    """Post model for individual messages in conversations."""
    
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    post_id = Column(Integer, nullable=False)  # Sequential ID within the conversation
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="posts")
    user = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post {self.post_id} in Conversation {self.conversation_id}>"