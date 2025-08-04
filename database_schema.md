# Database Schema Design

## Entity-Relationship Diagram (ERD)

```
+----------------+       +---------------------+       +---------------+
| Users          |       | Challenges          |       | Categories    |
+----------------+       +---------------------+       +---------------+
| id (PK)        |       | id (PK)             |       | id (PK)       |
| username       |       | challenge_id        |       | name          |
| email          |       | title               |       | description   |
| password_hash  |       | description         |       | created_at    |
| is_support     |       | category_id (FK)    |       | updated_at    |
| created_at     |       | difficulty_id (FK)  |       +---------------+
| updated_at     |       | points              |
+----------------+       | created_at          |       +---------------+
        |                | updated_at          |       | Difficulties  |
        |                +---------------------+       +---------------+
        |                        |                     | id (PK)       |
        |                        |                     | name          |
        |                        |                     | created_at    |
+----------------+               |                     | updated_at    |
| Conversations  |               |                     +---------------+
+----------------+               |
| id (PK)        |               |                     +---------------+
| identifier     |               |                     | Tags          |
| topic          |               |                     +---------------+
| category_id(FK)|               |                     | id (PK)       |
| challenge_id(FK)<---------------+                     | name          |
| created_at     |                                     | created_at    |
| updated_at     |                                     | updated_at    |
+----------------+                                     +---------------+
        |                                                     |
        |                                                     |
+----------------+                                     +---------------+
| Posts          |                                     | ChallengeTags |
+----------------+                                     +---------------+
| id (PK)        |                                     | id (PK)       |
| conversation_id|                                     | challenge_id  |
| post_id        |                                     | tag_id        |
| user_id (FK)   |                                     | created_at    |
| content        |                                     | updated_at    |
| timestamp      |                                     +---------------+
| created_at     |
| updated_at     |                                     +------------------+
+----------------+                                     | LearningObjectives|
                                                       +------------------+
                                                       | id (PK)          |
                                                       | challenge_id (FK)|
                                                       | description      |
                                                       | created_at       |
                                                       | updated_at       |
                                                       +------------------+

                                                       +---------------+
                                                       | Hints         |
                                                       +---------------+
                                                       | id (PK)       |
                                                       | challenge_id  |
                                                       | description   |
                                                       | created_at    |
                                                       | updated_at    |
                                                       +---------------+
```

## Tables Definition

### Users
- **id**: Primary key, auto-increment
- **username**: Unique username for the user
- **email**: User's email address
- **password_hash**: Hashed password for security
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
- **challenge_id**: Foreign key to Challenges table
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

## Normalization

This schema is normalized to the Third Normal Form (3NF):

1. **First Normal Form (1NF)**:
   - All tables have a primary key
   - All columns contain atomic values
   - No repeating groups

2. **Second Normal Form (2NF)**:
   - All tables are in 1NF
   - All non-key attributes are fully functionally dependent on the primary key
   - Separated tags, learning objectives, and hints into their own tables

3. **Third Normal Form (3NF)**:
   - All tables are in 2NF
   - No transitive dependencies
   - Categories and difficulties are in separate tables to avoid redundancy

## Design Decisions and Rationale

1. **Separate Users Table**:
   - Allows for authentication and authorization
   - Distinguishes between regular users and support team members
   - Enables user-specific features and permissions

2. **Normalized Category and Difficulty**:
   - Reduces data redundancy
   - Ensures consistency in category and difficulty names
   - Makes it easier to add, modify, or remove categories/difficulties

3. **Many-to-Many Relationship for Tags**:
   - Challenges can have multiple tags
   - Tags can be associated with multiple challenges
   - Junction table (ChallengeTags) implements this relationship

4. **Separate Tables for Learning Objectives and Hints**:
   - These are one-to-many relationships with challenges
   - Allows for flexible number of objectives and hints per challenge
   - Maintains data integrity and normalization

5. **Conversation and Posts Structure**:
   - Conversations are linked to challenges but maintained separately
   - Posts are linked to conversations in a one-to-many relationship
   - Preserves the hierarchical nature of the conversation threads

6. **Timestamps for Auditing**:
   - All tables include created_at and updated_at fields
   - Enables tracking of when records were created or modified
   - Useful for debugging, auditing, and data analysis

7. **Use of Foreign Keys**:
   - Maintains referential integrity
   - Prevents orphaned records
   - Enables efficient joins between related tables