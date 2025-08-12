import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlalchemy.orm import Session

from app.db.session import Base, postgres_engine, PostgresSessionLocal
from app.models import *  # Import all models to ensure they are registered with Base.metadata

logger = logging.getLogger(__name__)

# Paths to sample data files
SAMPLE_CHALLENGES_FILE = "sample_data_some_coding_challenges.json"
SAMPLE_CONVERSATIONS_FILE = "support_conversations.json"

def init_db(load_sample_data: bool = True, force_reload: bool = False):
    """
    Initialize the database by creating all tables defined in the models.
    Optionally load sample data from JSON files.
    
    Args:
        load_sample_data: If True, load sample data from JSON files
        force_reload: If True, load data even if some data already exists
    """
    try:
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=postgres_engine)
        logger.info("Database tables created successfully")
        
        # Load sample data if requested
        if load_sample_data:
            logger.info(f"Loading sample data (force_reload={force_reload})...")
            db = PostgresSessionLocal()
            try:
                load_sample_data_from_files(db, force_reload=force_reload)
                logger.info("Sample data loaded successfully")
            except Exception as e:
                logger.error(f"Error loading sample data: {e}")
                # Don't raise the exception, just log it
            finally:
                db.close()
    except ProgrammingError as e:
        logger.error(f"Error creating database tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing database: {e}")
        raise

def load_sample_data_from_files(db: Session, force_reload: bool = False):
    """
    Load sample data from JSON files into the database.
    
    Args:
        db: SQLAlchemy database session
        force_reload: If True, load data even if some data already exists
    """
    # Check if data is already loaded
    challenge_count = db.query(Challenge).count()
    conversation_count = db.query(Conversation).count()
    
    if not force_reload and (challenge_count > 0 or conversation_count > 0):
        logger.info(f"Sample data already loaded (Challenges: {challenge_count}, Conversations: {conversation_count}), skipping...")
        return
    
    logger.info(f"Loading sample data (force_reload={force_reload})...")
    
    # Load challenges data
    challenges_data = load_json_file(SAMPLE_CHALLENGES_FILE)
    if challenges_data:
        load_challenges(db, challenges_data)
    
    # Load conversations data
    conversations_data = load_json_file(SAMPLE_CONVERSATIONS_FILE)
    if conversations_data:
        load_conversations(db, conversations_data)

def load_json_file(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        filename: Name of the JSON file to load
        
    Returns:
        Parsed JSON data or None if file not found or invalid
    """
    try:
        file_path = Path(filename)
        if not file_path.exists():
            logger.warning(f"Sample data file not found: {filename}")
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded data from {filename}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {filename}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading {filename}: {e}")
        return None

def load_challenges(db: Session, data: Dict[str, Any]):
    """
    Load challenge data into the database.
    
    Args:
        db: SQLAlchemy database session
        data: Challenge data from JSON file
    """
    if 'coding_challenges' not in data:
        logger.warning("No coding_challenges found in data")
        return
    
    challenges = data['coding_challenges']
    logger.info(f"Loading {len(challenges)} challenges")
    
    # Debug: Print the challenge IDs to see what's being loaded
    challenge_ids = [c.get('challenge_id') for c in challenges]
    logger.info(f"Challenge IDs to load: {challenge_ids}")
    
    # Check if challenges already exist
    existing_challenge_count = db.query(Challenge).count()
    if existing_challenge_count > 0:
        logger.warning(f"Found {existing_challenge_count} existing challenges. Clearing them first...")
        try:
            # Delete existing challenges and related data
            db.query(ChallengeTag).delete()
            db.query(LearningObjective).delete()
            db.query(Hint).delete()
            db.query(Challenge).delete()
            db.commit()
            logger.info("Cleared existing challenges and related data")
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing existing challenges: {e}")
            raise
    
    # Create categories and difficulties first
    categories = {}
    difficulties = {}
    tags = {}
    
    # Process all challenges to extract unique categories, difficulties, and tags
    for challenge_data in challenges:
        # Extract category
        category_name = challenge_data.get('category')
        if category_name and category_name not in categories:
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Category for {category_name}")
                db.add(category)
                try:
                    db.flush()  # Flush to get the ID without committing
                    logger.info(f"Created category: {category_name}")
                except IntegrityError:
                    db.rollback()
                    category = db.query(Category).filter(Category.name == category_name).first()
                    logger.info(f"Using existing category: {category_name}")
            categories[category_name] = category
        
        # Extract difficulty
        difficulty_name = challenge_data.get('difficulty')
        if difficulty_name and difficulty_name not in difficulties:
            difficulty = db.query(Difficulty).filter(Difficulty.name == difficulty_name).first()
            if not difficulty:
                difficulty = Difficulty(name=difficulty_name)
                db.add(difficulty)
                try:
                    db.flush()  # Flush to get the ID without committing
                    logger.info(f"Created difficulty: {difficulty_name}")
                except IntegrityError:
                    db.rollback()
                    difficulty = db.query(Difficulty).filter(Difficulty.name == difficulty_name).first()
                    logger.info(f"Using existing difficulty: {difficulty_name}")
            difficulties[difficulty_name] = difficulty
        
        # Extract tags
        challenge_tags = challenge_data.get('tags', [])
        for tag_name in challenge_tags:
            if tag_name and tag_name not in tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    try:
                        db.flush()  # Flush to get the ID without committing
                        logger.info(f"Created tag: {tag_name}")
                    except IntegrityError:
                        db.rollback()
                        tag = db.query(Tag).filter(Tag.name == tag_name).first()
                        logger.info(f"Using existing tag: {tag_name}")
                tags[tag_name] = tag
    
    # Commit categories, difficulties, and tags
    try:
        db.commit()
        logger.info("Committed categories, difficulties, and tags")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing categories, difficulties, and tags: {e}")
        raise
    
    # Now create challenges with their relationships
    challenge_count = 0
    error_count = 0
    
    # Log all challenge IDs we're about to process
    for i, challenge_data in enumerate(challenges):
        logger.info(f"Challenge {i+1}/{len(challenges)}: {challenge_data.get('challenge_id')}")
    
    for challenge_data in challenges:
        try:
            challenge_id = challenge_data.get('challenge_id')
            logger.info(f"Processing challenge: {challenge_id}")
            
            # Get category and difficulty
            category_name = challenge_data.get('category')
            difficulty_name = challenge_data.get('difficulty')
            logger.info(f"  Category: {category_name}, Difficulty: {difficulty_name}")
            
            if not category_name or not difficulty_name:
                logger.warning(f"Skipping challenge {challenge_id} due to missing category or difficulty")
                continue
            
            category = categories.get(category_name)
            difficulty = difficulties.get(difficulty_name)
            
            if not category:
                logger.warning(f"Category {category_name} not found for challenge {challenge_id}")
                continue
                
            if not difficulty:
                logger.warning(f"Difficulty {difficulty_name} not found for challenge {challenge_id}")
                continue
                
            logger.info(f"  Found category ID: {category.id}, difficulty ID: {difficulty.id}")
            
            # Create challenge
            # Handle points field - convert to int safely
            points_value = challenge_data.get('points', 0)
            logger.info(f"  Points value (raw): '{points_value}' (type: {type(points_value).__name__})")
            try:
                points = int(points_value)
                logger.info(f"  Points converted to int: {points}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid points value '{points_value}' for challenge {challenge_id}, using 0 instead: {e}")
                points = 0
            
            title = challenge_data.get('title')
            description = challenge_data.get('description')
            logger.info(f"  Creating challenge: {challenge_id} - '{title}'")
                
            challenge = Challenge(
                challenge_id=challenge_id,
                title=title,
                description=description,
                category_id=category.id,
                difficulty_id=difficulty.id,
                points=points
            )
            db.add(challenge)
            logger.info(f"  Added challenge to session, flushing...")
            db.flush()  # Flush to get the ID without committing
            logger.info(f"  Challenge flushed, got ID: {challenge.id}")
            
            # Add learning objectives
            learning_objectives = challenge_data.get('learning_objectives', [])
            logger.info(f"  Adding {len(learning_objectives)} learning objectives")
            for objective in learning_objectives:
                learning_objective = LearningObjective(
                    challenge_id=challenge.id,
                    description=objective
                )
                db.add(learning_objective)
            
            # Add hints
            hints = challenge_data.get('hints', [])
            logger.info(f"  Adding {len(hints)} hints")
            for hint in hints:
                hint_obj = Hint(
                    challenge_id=challenge.id,
                    description=hint
                )
                db.add(hint_obj)
            
            # Add tags
            challenge_tags = challenge_data.get('tags', [])
            logger.info(f"  Adding {len(challenge_tags)} tags")
            tag_count = 0
            for tag_name in challenge_tags:
                tag = tags.get(tag_name)
                if tag:
                    challenge_tag = ChallengeTag(
                        challenge_id=challenge.id,
                        tag_id=tag.id
                    )
                    db.add(challenge_tag)
                    tag_count += 1
                else:
                    logger.warning(f"  Tag '{tag_name}' not found in tags dictionary")
            logger.info(f"  Added {tag_count} tags successfully")
            
            # Commit each challenge individually to avoid losing all if one fails
            logger.info(f"  Committing challenge {challenge_id} to database...")
            db.commit()
            challenge_count += 1
            logger.info(f"  SUCCESS: Created challenge: {challenge.challenge_id} - {challenge.title}")
        except Exception as e:
            db.rollback()
            error_count += 1
            logger.error(f"Error creating challenge {challenge_data.get('challenge_id')}: {e}")
            logger.error(f"Challenge data: {challenge_data}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Continue with next challenge
    
    logger.info(f"Challenge loading completed. Created {challenge_count} challenges with {error_count} errors.")

def load_conversations(db: Session, data: Dict[str, Any]):
    """
    Load conversation data into the database.
    
    Args:
        db: SQLAlchemy database session
        data: Conversation data from JSON file
    """
    if 'support_conversations' not in data:
        logger.warning("No support_conversations found in data")
        return
    
    conversations = data['support_conversations']
    logger.info(f"Loading {len(conversations)} conversations")
    
    # Check if conversations already exist
    existing_conversation_count = db.query(Conversation).count()
    existing_post_count = db.query(Post).count()
    if existing_conversation_count > 0 or existing_post_count > 0:
        logger.warning(f"Found {existing_conversation_count} existing conversations and {existing_post_count} posts. Clearing them first...")
        try:
            # Delete existing conversations and posts
            db.query(Post).delete()
            db.query(Conversation).delete()
            db.commit()
            logger.info("Cleared existing conversations and posts")
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing existing conversations: {e}")
            raise
    
    # Create or get support users first
    users = {}
    
    # Process all conversations to extract unique users
    for conversation_data in conversations:
        posts = conversation_data.get('posts', [])
        for post in posts:
            username = post.get('user')
            if username and username not in users:
                user = db.query(User).filter(User.username == username).first()
                if not user:
                    # Create a new user with a default email and password
                    is_support = 'support' in username.lower() or 'team' in username.lower() or 'helper' in username.lower()
                    email = f"{username}@example.com"
                    password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # hash of 'password'
                    
                    user = User(
                        username=username,
                        email=email,
                        password_hash=password_hash,
                        is_support=is_support
                    )
                    db.add(user)
                    try:
                        db.flush()  # Flush to get the ID without committing
                        logger.info(f"Created user: {username}")
                    except IntegrityError:
                        db.rollback()
                        user = db.query(User).filter(User.username == username).first()
                        logger.info(f"Using existing user: {username}")
                users[username] = user
    
    # Commit users
    try:
        db.commit()
        logger.info("Committed users")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing users: {e}")
        raise
    
    # Now create conversations with their posts
    conversation_count = 0
    post_count = 0
    error_count = 0
    
    # First, make sure we have challenges loaded
    challenge_count = db.query(Challenge).count()
    if challenge_count == 0:
        logger.warning("No challenges found in database. Conversations require challenges to be loaded first.")
        return
    
    for conversation_data in conversations:
        try:
            # Get challenge and category
            challenge_id_str = conversation_data.get('challenge_id')
            category_name = conversation_data.get('category')
            
            if not challenge_id_str or not category_name:
                logger.warning(f"Skipping conversation {conversation_data.get('identifier')} due to missing challenge_id or category")
                continue
            
            # Find the challenge
            challenge = db.query(Challenge).filter(Challenge.challenge_id == challenge_id_str).first()
            if not challenge:
                logger.warning(f"Challenge {challenge_id_str} not found for conversation {conversation_data.get('identifier')}")
                continue
            
            # Find or create the category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Category for {category_name}")
                db.add(category)
                db.flush()
                logger.info(f"Created category: {category_name}")
            
            # Create conversation
            conversation = Conversation(
                identifier=conversation_data.get('identifier'),
                topic=conversation_data.get('topic'),
                category_id=category.id,
                challenge_id=challenge.id
            )
            db.add(conversation)
            db.flush()  # Flush to get the ID without committing
            
            # Add posts
            conversation_posts = []
            for post_data in conversation_data.get('posts', []):
                username = post_data.get('user')
                user = users.get(username)
                if not user:
                    logger.warning(f"User {username} not found for post in conversation {conversation.identifier}")
                    continue
                
                # Parse timestamp
                timestamp_str = post_data.get('timestamp')
                try:
                    timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    timestamp = datetime.datetime.utcnow()
                
                post = Post(
                    conversation_id=conversation.id,
                    post_id=post_data.get('post_id', 0),
                    user_id=user.id,
                    content=post_data.get('content', ''),
                    timestamp=timestamp
                )
                db.add(post)
                conversation_posts.append(post)
            
            # Commit each conversation individually to avoid losing all if one fails
            db.commit()
            conversation_count += 1
            post_count += len(conversation_posts)
            logger.info(f"Created conversation: {conversation.identifier} - {conversation.topic} with {len(conversation_posts)} posts")
        except Exception as e:
            db.rollback()
            error_count += 1
            logger.error(f"Error creating conversation {conversation_data.get('identifier')}: {e}")
            logger.error(f"Conversation data: {conversation_data}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Continue with next conversation
    
    logger.info(f"Conversation loading completed. Created {conversation_count} conversations with {post_count} posts. Encountered {error_count} errors.")