from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.conversation_models import Conversation, Post
from app.schemas.conversation import ConversationCreate, ConversationUpdate, PostCreate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    """
    CRUD operations for Conversation model.
    """

    def get_by_identifier(self, db: Session, *, identifier: str) -> Optional[Conversation]:
        """
        Get a conversation by its unique identifier.
        """
        return db.query(Conversation).filter(Conversation.identifier == identifier).first()

    def create(self, db: Session, *, obj_in: ConversationCreate, user_id: int, challenge_id: int = None) -> Conversation:
        """
        Create a new conversation with an initial post.
        
        Args:
            db: Database session
            obj_in: Conversation data
            user_id: User ID for the initial post
            challenge_id: Optional integer challenge ID to override the string challenge_id in obj_in
        """
        # Generate a unique identifier
        last_conversation = db.query(Conversation).order_by(Conversation.id.desc()).first()
        if last_conversation:
            # Extract the number from the last identifier and increment
            last_num = int(last_conversation.identifier.split("_")[1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        identifier = f"CONV_{new_num:03d}"
        
        # Create the conversation
        conversation_data = obj_in.model_dump(exclude={"initial_post", "identifier", "challenge_id"})
        db_obj = Conversation(
            identifier=identifier,
            challenge_id=challenge_id,  # Use the provided integer challenge_id
            **conversation_data
        )
        db.add(db_obj)
        db.flush()  # Flush to get the ID without committing
        
        # Add the initial post
        if obj_in.initial_post:
            self._add_post(
                db, 
                conversation=db_obj, 
                content=obj_in.initial_post, 
                user_id=user_id
            )
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_post(self, db: Session, *, conversation_id: str, post_in: PostCreate, user_id: int) -> Post:
        """
        Add a post to a conversation.
        """
        conversation = self.get_by_identifier(db, identifier=conversation_id)
        if not conversation:
            return None
        
        post = self._add_post(
            db, 
            conversation=conversation, 
            content=post_in.content, 
            user_id=user_id
        )
        
        db.commit()
        db.refresh(post)
        return post

    def get_posts(self, db: Session, *, conversation_id: str) -> List[Post]:
        """
        Get all posts for a specific conversation.
        """
        conversation = self.get_by_identifier(db, identifier=conversation_id)
        if not conversation:
            return []
        
        return db.query(Post).filter(Post.conversation_id == conversation.id).order_by(Post.post_id).all()

    def filter_conversations(
        self, db: Session, *, category_id: Optional[int] = None, challenge_id: Optional[int] = None, 
        user_id: Optional[int] = None, search: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """
        Filter conversations based on various criteria.
        """
        query = db.query(Conversation)
        
        if category_id:
            query = query.filter(Conversation.category_id == category_id)
        
        if challenge_id:
            query = query.filter(Conversation.challenge_id == challenge_id)
        
        if user_id:
            # Filter by conversations where the user has posted
            query = query.join(Post).filter(Post.user_id == user_id).distinct()
        
        if search:
            # Search in topic and posts content
            search_term = f"%{search}%"
            query = query.filter(Conversation.topic.ilike(search_term))
            # Or search in posts
            query = query.union(
                db.query(Conversation)
                .join(Post)
                .filter(Post.content.ilike(search_term))
            )
        
        return query.offset(skip).limit(limit).all()

    def _add_post(self, db: Session, *, conversation: Conversation, content: str, user_id: int) -> Post:
        """
        Add a post to a conversation (internal helper method).
        """
        # Get the next post_id for this conversation
        last_post = db.query(Post).filter(Post.conversation_id == conversation.id).order_by(Post.post_id.desc()).first()
        if last_post:
            post_id = last_post.post_id + 1
        else:
            post_id = 1
        
        # Create the post
        post = Post(
            conversation_id=conversation.id,
            post_id=post_id,
            user_id=user_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.add(post)
        return post


# Create a singleton instance
conversation = CRUDConversation(Conversation)