from app.schemas.base import BaseSchema
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, User, UserWithPosts
)
from app.schemas.challenge import (
    TagBase, TagCreate, Tag,
    LearningObjectiveBase, LearningObjectiveCreate, LearningObjective,
    HintBase, HintCreate, Hint,
    CategoryBase, CategoryCreate, Category,
    DifficultyBase, DifficultyCreate, Difficulty,
    ChallengeBase, ChallengeCreate, ChallengeUpdate, Challenge, ChallengeFilter
)
from app.schemas.conversation import (
    PostBase, PostCreate, Post,
    ConversationBase, ConversationCreate, ConversationUpdate, Conversation, ConversationFilter
)

# Export all schemas
__all__ = [
    # Base
    "BaseSchema",
    
    # User
    "UserBase", "UserCreate", "UserUpdate", "User", "UserWithPosts",
    
    # Challenge
    "TagBase", "TagCreate", "Tag",
    "LearningObjectiveBase", "LearningObjectiveCreate", "LearningObjective",
    "HintBase", "HintCreate", "Hint",
    "CategoryBase", "CategoryCreate", "Category",
    "DifficultyBase", "DifficultyCreate", "Difficulty",
    "ChallengeBase", "ChallengeCreate", "ChallengeUpdate", "Challenge", "ChallengeFilter",
    
    # Conversation
    "PostBase", "PostCreate", "Post",
    "ConversationBase", "ConversationCreate", "ConversationUpdate", "Conversation", "ConversationFilter"
]