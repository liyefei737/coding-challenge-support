from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.db.session import Base


class BaseModel(Base):
    """Base model for all database models with common fields and behaviors."""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)