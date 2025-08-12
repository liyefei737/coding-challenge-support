from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session

from app.crud import challenge
from app.db.session import get_postgres_db
from app.models.basic_models import Category, Difficulty
from app.schemas import (
    Challenge, ChallengeCreate, ChallengeUpdate, ChallengeFilter,
    Conversation
)

# Fixed user ID for operations that need a user ID
FIXED_USER_ID = 1

router = APIRouter()

@router.get("/", response_model=List[Challenge])
def get_challenges(
    db: Session = Depends(get_postgres_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    difficulty_id: Optional[int] = None,
    search: Optional[str] = None,
    min_points: Optional[int] = None,
    max_points: Optional[int] = None,
    tags: Optional[List[str]] = Query(None),
) -> Any:
    """
    Retrieve all challenges with optional filtering.
    """
    filter_params = ChallengeFilter(
        category_id=category_id,
        difficulty_id=difficulty_id,
        search=search,
        min_points=min_points,
        max_points=max_points,
        tags=tags,
    )
    challenges_list = challenge.filter_challenges(
        db, filter_params=filter_params, skip=skip, limit=limit
    )
    return challenges_list

@router.post("/", response_model=Challenge)
def create_challenge(
    *,
    db: Session = Depends(get_postgres_db),
    challenge_in: ChallengeCreate = Body(...),
) -> Any:
    """
    Create a new challenge.
    """
    # Check if category exists
    if not db.query(Category).filter(Category.id == challenge_in.category_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Category not found"
        )
    
    # Check if difficulty exists
    if not db.query(Difficulty).filter(Difficulty.id == challenge_in.difficulty_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Difficulty not found"
        )
    
    # Check if challenge_id already exists
    if challenge.get_by_challenge_id(db, challenge_id=challenge_in.challenge_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Challenge ID already exists"
        )
    
    return challenge.create(db, obj_in=challenge_in)

@router.get("/{challenge_id}", response_model=Challenge)
def get_challenge(
    *,
    db: Session = Depends(get_postgres_db),
    challenge_id: str,
) -> Any:
    """
    Get a specific challenge by ID.
    """
    db_challenge = challenge.get_by_challenge_id(db, challenge_id=challenge_id)
    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Challenge not found"
        )
    return db_challenge

@router.put("/{challenge_id}", response_model=Challenge)
def update_challenge(
    *,
    db: Session = Depends(get_postgres_db),
    challenge_id: str,
    challenge_in: ChallengeUpdate = Body(...),
) -> Any:
    """
    Update a challenge.
    """
    db_challenge = challenge.get_by_challenge_id(db, challenge_id=challenge_id)
    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Challenge not found"
        )
    
    # Check if category exists if provided
    if challenge_in.category_id is not None:
        if not db.query(Category).filter(Category.id == challenge_in.category_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Category not found"
            )
    
    # Check if difficulty exists if provided
    if challenge_in.difficulty_id is not None:
        if not db.query(Difficulty).filter(Difficulty.id == challenge_in.difficulty_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Difficulty not found"
            )
    
    return challenge.update(db, db_obj=db_challenge, obj_in=challenge_in)

@router.delete("/{challenge_id}", response_model=Challenge)
def delete_challenge(
    *,
    db: Session = Depends(get_postgres_db),
    challenge_id: str,
) -> Any:
    """
    Delete a challenge.
    """
    db_challenge = challenge.get_by_challenge_id(db, challenge_id=challenge_id)
    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Challenge not found"
        )
    return challenge.remove(db, id=db_challenge.id)

@router.get("/{challenge_id}/conversations", response_model=List[Conversation])
def get_challenge_conversations(
    *,
    db: Session = Depends(get_postgres_db),
    challenge_id: str,
) -> Any:
    """
    Get all conversations for a specific challenge.
    """
    db_challenge = challenge.get_by_challenge_id(db, challenge_id=challenge_id)
    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Challenge not found"
        )
    
    # Get all conversations for the challenge
    conversations = challenge.get_conversations(db, challenge_id=challenge_id)
    
    return conversations