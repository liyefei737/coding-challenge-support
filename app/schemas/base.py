from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema for all API schemas with common fields."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model -> Pydantic model conversion
        populate_by_name=True  # Allow populating by field name as well as alias
    )