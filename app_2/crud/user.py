from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.basic_models import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    """

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get a user by username.
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.
        """
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=obj_in.password,  # Store password directly without hashing
            is_support=obj_in.is_support,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
            if "password" in update_data:
                update_data["password_hash"] = update_data["password"]  # Store password directly
                del update_data["password"]
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["password_hash"] = update_data["password"]  # Store password directly
                del update_data["password"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def is_support(self, user: User) -> bool:
        """
        Check if a user is a support team member.
        """
        return user.is_support


# Create a singleton instance
user = CRUDUser(User)