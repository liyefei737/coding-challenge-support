# Coding Challenges Platform

A FastAPI-based application for managing coding challenges and support conversations.

## Project Overview

This application provides an API for:
- Managing coding challenges with categories, difficulties, and tags
- Support conversations related to challenges
- No authentication required (all requests are assumed to be authenticated)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. No additional installation steps are needed as the application runs in Docker containers.

## Running the Application

### Using Docker Compose

1. Start the application and databases:
   ```bash
   docker-compose up
   ```

   This command will:
   - Build the application container
   - Start PostgreSQL database
   - Start the FastAPI application with hot-reload enabled

2. To run in detached mode (background):
   ```bash
   docker-compose up -d
   ```

3. To stop the application:
   ```bash
   docker-compose down
   ```

4. To stop the application and remove volumes:
   ```bash
   docker-compose down -v
   ```

### Accessing the Application

Once running, the application is available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- OpenAPI Specification: http://localhost:8000/openapi.json

## API Documentation

The API documentation is available at http://localhost:8000/docs when the application is running.

Key endpoints include:
- `/api/v1/challenges`: Manage coding challenges
- `/api/v1/conversations`: Manage support conversations
- `/api/v1/users`: User management
- `/health`: Health check endpoint

## Database Information

The application uses PostgreSQL as the database for storing challenges, users, and other data.

Database credentials are configured in the `docker-compose.yml` file.

## Development

### Project Structure

```
app/
├── api/                # API routes and dependencies
│   ├── v1/             # API version 1
│   │   ├── endpoints/  # API endpoints
├── core/               # Core application settings
├── crud/               # Database CRUD operations
├── db/                 # Database session management
├── models/             # Database models
├── schemas/            # Pydantic schemas for validation
```

### Sample Data

The repository includes sample data files:
- `sample_data_some_coding_challenges.json`: Sample coding challenges
- `support_conversations.json`: Sample support conversations

## Troubleshooting

If you encounter issues:

1. Check if all containers are running:
   ```bash
   docker-compose ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs
   ```

3. Check specific service logs:
   ```bash
   docker-compose logs app
   docker-compose logs postgres
   ```

4. Ensure database health checks are passing:
   ```bash
   docker-compose ps postgres
   ```