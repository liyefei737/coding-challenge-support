from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from app.db.session import get_postgres_db
from app.crud import conversation, challenge, user
from app.models.basic_models import Category, User
from app.schemas import (
    Conversation, ConversationCreate, ConversationUpdate, ConversationFilter,
    Post, PostCreate
)

# Fixed user ID for operations that need a user ID
FIXED_USER_ID = 1

router = APIRouter()

@router.get("/", response_model=List[Conversation])
def get_conversations(
    db: Session = Depends(get_postgres_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    challenge_id: Optional[int] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Retrieve all conversations with optional filtering.
    """
    # If user_id is not provided, use all conversations
    # No filtering based on user privileges
    
    conversations_list = conversation.filter_conversations(
        db, 
        category_id=category_id,
        challenge_id=challenge_id,
        user_id=user_id,
        search=search,
        skip=skip, 
        limit=limit
    )
    return conversations_list

@router.post("/", response_model=Conversation)
def create_conversation(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_in: ConversationCreate = Body(...),
) -> Any:
    """
    Create a new conversation.
    """
    # Check if category exists
    if not db.query(Category).filter(Category.id == conversation_in.category_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Category not found"
        )
    
    # Check if challenge exists
    db_challenge = challenge.get_by_challenge_id(db, challenge_id=conversation_in.challenge_id)
    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Challenge not found"
        )
    
    # Create conversation using fixed user ID and the challenge's id
    return conversation.create(db, obj_in=conversation_in, user_id=FIXED_USER_ID, challenge_id=db_challenge.id)

@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_id: str,
) -> Any:
    """
    Get a specific conversation by ID.
    """
    db_conversation = conversation.get_by_identifier(db, identifier=conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    return db_conversation

@router.put("/{conversation_id}", response_model=Conversation)
def update_conversation(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_id: str,
    conversation_in: ConversationUpdate = Body(...),
) -> Any:
    """
    Update a conversation.
    """
    db_conversation = conversation.get_by_identifier(db, identifier=conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    # Check if category exists if provided
    if conversation_in.category_id is not None:
        if not db.query(Category).filter(Category.id == conversation_in.category_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Category not found"
            )
    
    # Check if challenge exists if provided
    if conversation_in.challenge_id is not None:
        db_challenge = challenge.get_by_challenge_id(db, challenge_id=conversation_in.challenge_id)
        if not db_challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Challenge not found"
            )
    
    return conversation.update(db, db_obj=db_conversation, obj_in=conversation_in)

@router.delete("/{conversation_id}", response_model=Conversation)
def delete_conversation(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_id: str,
) -> Any:
    """
    Delete a conversation.
    """
    db_conversation = conversation.get_by_identifier(db, identifier=conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    return conversation.remove(db, id=db_conversation.id)

@router.get("/{conversation_id}/posts", response_model=List[Post])
def get_conversation_posts(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_id: str,
) -> Any:
    """
    Get all posts for a specific conversation.
    """
    db_conversation = conversation.get_by_identifier(db, identifier=conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    posts = conversation.get_posts(db, conversation_id=conversation_id)
    return posts

@router.post("/{conversation_id}/posts", response_model=Post)
def create_post(
    *,
    db: Session = Depends(get_postgres_db),
    conversation_id: str,
    post_in: PostCreate = Body(...),
) -> Any:
    """
    Add a post to a conversation.
    """
    db_conversation = conversation.get_by_identifier(db, identifier=conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Conversation not found"
        )
    
    post = conversation.add_post(
        db, 
        conversation_id=conversation_id, 
        post_in=post_in, 
        user_id=FIXED_USER_ID
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Failed to create post"
        )
    
    return post