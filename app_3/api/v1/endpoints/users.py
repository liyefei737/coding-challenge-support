from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.crud import user
from app.db.session import get_postgres_db
from app.schemas import (
    User, UserCreate, UserUpdate, UserWithPosts
)

# Fixed user ID for operations that need a user ID
FIXED_USER_ID = 1

router = APIRouter()


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_postgres_db),
    user_in: UserCreate = Body(...),
) -> Any:
    """
    Create a new user.
    """
    # Check if username already exists
    if user.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    if user.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    return user.create(db, obj_in=user_in)


@router.get("/me", response_model=User)
def read_users_me(
    db: Session = Depends(get_postgres_db),
) -> Any:
    """
    Get current user.
    """
    # Use fixed user ID instead of authentication
    current_user = user.get(db, id=FIXED_USER_ID)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_postgres_db),
    user_in: UserUpdate = Body(...),
) -> Any:
    """
    Update current user.
    """
    # Use fixed user ID instead of authentication
    current_user = user.get(db, id=FIXED_USER_ID)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if username already exists
    if user_in.username and user_in.username != current_user.username:
        if user.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Check if email already exists
    if user_in.email and user_in.email != current_user.email:
        if user.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    return user.update(db, db_obj=current_user, obj_in=user_in)


@router.get("/{user_id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_postgres_db),
    user_id: int,
) -> Any:
    """
    Get a specific user by ID.
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return db_user


@router.get("/{user_id}/posts", response_model=UserWithPosts)
def read_user_posts(
    *,
    db: Session = Depends(get_postgres_db),
    user_id: int,
) -> Any:
    """
    Get a specific user with their posts.
    """
    # Get the user from the database
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Explicitly load the posts relationship
    db.refresh(db_user)
    
    # Create a UserWithPosts response
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "is_support": db_user.is_support,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "posts": db_user.posts
    }