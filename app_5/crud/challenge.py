from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.basic_models import Tag
from app.models.challenge_models import Challenge, ChallengeTag, LearningObjective, Hint
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate, ChallengeFilter


class CRUDChallenge(CRUDBase[Challenge, ChallengeCreate, ChallengeUpdate]):
    """
    CRUD operations for Challenge model.
    """

    def get_by_challenge_id(self, db: Session, *, challenge_id: str) -> Optional[Challenge]:
        """
        Get a challenge by its unique challenge_id.
        """
        return db.query(Challenge).filter(Challenge.challenge_id == challenge_id).first()

    def create(self, db: Session, *, obj_in: ChallengeCreate) -> Challenge:
        """
        Create a new challenge with related entities (tags, learning objectives, hints).
        """
        # Create the challenge
        challenge_data = obj_in.model_dump(exclude={"tags", "learning_objectives", "hints"})
        db_obj = Challenge(**challenge_data)
        db.add(db_obj)
        db.flush()  # Flush to get the ID without committing

        # Add tags
        if obj_in.tags:
            self._add_tags(db, db_obj, obj_in.tags)

        # Add learning objectives
        if obj_in.learning_objectives:
            self._add_learning_objectives(db, db_obj, obj_in.learning_objectives)

        # Add hints
        if obj_in.hints:
            self._add_hints(db, db_obj, obj_in.hints)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Challenge,
        obj_in: Union[ChallengeUpdate, Dict[str, Any]]
    ) -> Challenge:
        """
        Update a challenge and its related entities.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
            tags = update_data.pop("tags", None)
            learning_objectives = update_data.pop("learning_objectives", None)
            hints = update_data.pop("hints", None)
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            tags = update_data.pop("tags", None)
            learning_objectives = update_data.pop("learning_objectives", None)
            hints = update_data.pop("hints", None)

        # Update the challenge
        db_obj = super().update(db, db_obj=db_obj, obj_in=update_data)

        # Update tags if provided
        if tags is not None:
            self._update_tags(db, db_obj, tags)

        # Update learning objectives if provided
        if learning_objectives is not None:
            self._update_learning_objectives(db, db_obj, learning_objectives)

        # Update hints if provided
        if hints is not None:
            self._update_hints(db, db_obj, hints)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def filter_challenges(
        self, db: Session, *, filter_params: ChallengeFilter, skip: int = 0, limit: int = 100
    ) -> List[Challenge]:
        """
        Filter challenges based on various criteria.
        """
        query = db.query(Challenge)

        if filter_params.category_id:
            query = query.filter(Challenge.category_id == filter_params.category_id)

        if filter_params.difficulty_id:
            query = query.filter(Challenge.difficulty_id == filter_params.difficulty_id)

        if filter_params.min_points is not None:
            query = query.filter(Challenge.points >= filter_params.min_points)

        if filter_params.max_points is not None:
            query = query.filter(Challenge.points <= filter_params.max_points)

        if filter_params.tags:
            # Filter by tags (challenges that have all the specified tags)
            for tag_name in filter_params.tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if tag:
                    query = query.join(ChallengeTag).filter(ChallengeTag.tag_id == tag.id)

        if filter_params.search:
            # Search in title and description
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                (Challenge.title.ilike(search_term)) | (Challenge.description.ilike(search_term))
            )

        return query.offset(skip).limit(limit).all()

    def get_conversations(self, db: Session, *, challenge_id: str) -> List[Any]:
        """
        Get all conversations for a specific challenge.
        """
        challenge = self.get_by_challenge_id(db, challenge_id=challenge_id)
        if not challenge:
            return []
        return challenge.conversations

    def _add_tags(self, db: Session, challenge: Challenge, tag_names: List[str]) -> None:
        """
        Add tags to a challenge.
        """
        for tag_name in tag_names:
            # Get or create the tag
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()

            # Create the challenge-tag relationship
            challenge_tag = ChallengeTag(challenge_id=challenge.id, tag_id=tag.id)
            db.add(challenge_tag)

    def _update_tags(self, db: Session, challenge: Challenge, tag_names: List[str]) -> None:
        """
        Update the tags for a challenge.
        """
        # Remove existing tags
        db.query(ChallengeTag).filter(ChallengeTag.challenge_id == challenge.id).delete()
        db.flush()

        # Add new tags
        self._add_tags(db, challenge, tag_names)

    def _add_learning_objectives(self, db: Session, challenge: Challenge, objectives: List[str]) -> None:
        """
        Add learning objectives to a challenge.
        """
        for objective in objectives:
            learning_objective = LearningObjective(
                challenge_id=challenge.id,
                description=objective
            )
            db.add(learning_objective)

    def _update_learning_objectives(self, db: Session, challenge: Challenge, objectives: List[str]) -> None:
        """
        Update the learning objectives for a challenge.
        """
        # Remove existing learning objectives
        db.query(LearningObjective).filter(LearningObjective.challenge_id == challenge.id).delete()
        db.flush()

        # Add new learning objectives
        self._add_learning_objectives(db, challenge, objectives)

    def _add_hints(self, db: Session, challenge: Challenge, hints: List[str]) -> None:
        """
        Add hints to a challenge.
        """
        for hint_text in hints:
            hint = Hint(
                challenge_id=challenge.id,
                description=hint_text
            )
            db.add(hint)

    def _update_hints(self, db: Session, challenge: Challenge, hints: List[str]) -> None:
        """
        Update the hints for a challenge.
        """
        # Remove existing hints
        db.query(Hint).filter(Hint.challenge_id == challenge.id).delete()
        db.flush()

        # Add new hints
        self._add_hints(db, challenge, hints)


# Create a singleton instance
challenge = CRUDChallenge(Challenge)