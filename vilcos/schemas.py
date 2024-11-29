from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    roles: list[RoleSchema]
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
