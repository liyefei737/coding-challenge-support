# Database Schema Design

**Last Updated: 2025-08-04**

## Tables Definition

### Users

- **id**: Primary key, auto-increment
- **username**: Unique username for the user (must be alphanumeric)
- **email**: User's email address
- **password_hash**: Password hashed using SHA-256 for security
- **is_support**: Boolean flag to identify support team members
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Categories

- **id**: Primary key, auto-increment
- **name**: Name of the category
- **description**: Optional description of the category
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Difficulties

- **id**: Primary key, auto-increment
- **name**: Name of the difficulty level (e.g., Beginner, Intermediate, Advanced)
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Tags

- **id**: Primary key, auto-increment
- **name**: Name of the tag
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Challenges

- **id**: Primary key, auto-increment
- **challenge_id**: Unique identifier for the challenge (e.g., CHAL_001)
- **title**: Title of the challenge
- **description**: Description of the challenge
- **category_id**: Foreign key to Categories table
- **difficulty_id**: Foreign key to Difficulties table
- **points**: Points awarded for completing the challenge
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### ChallengeTags

- **id**: Primary key, auto-increment
- **challenge_id**: Foreign key to Challenges table
- **tag_id**: Foreign key to Tags table
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### LearningObjectives

- **id**: Primary key, auto-increment
- **challenge_id**: Foreign key to Challenges table
- **description**: Description of the learning objective
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Hints

- **id**: Primary key, auto-increment
- **challenge_id**: Foreign key to Challenges table
- **description**: Content of the hint
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Conversations

- **id**: Primary key, auto-increment
- **identifier**: Unique identifier for the conversation (e.g., CONV_001)
- **topic**: Topic of the conversation
- **category_id**: Foreign key to Categories table
- **challenge_id**: Foreign key to Challenges table (references the id column, not the challenge_id string)
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Posts

- **id**: Primary key, auto-increment
- **conversation_id**: Foreign key to Conversations table
- **post_id**: Sequential ID of the post within the conversation
- **user_id**: Foreign key to Users table
- **content**: Content of the post
- **timestamp**: Timestamp when the post was created
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated