from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# PostgreSQL engine
postgres_engine = create_engine(
    str(settings.POSTGRES_URI),
    pool_pre_ping=True,
    echo=True,
)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session
def get_postgres_db():
    """
    Dependency function to get a PostgreSQL database session.
    To be used with FastAPI dependency injection.
    """
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()