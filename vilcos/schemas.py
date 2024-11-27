from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
