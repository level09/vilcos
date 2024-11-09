from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    item_number: int
    name: str
    name_korean: Optional[str] = None
    description: Optional[str] = None
    dietary_info: Optional[str] = None
    price: float
    category_id: int

class ItemResponse(BaseModel):
    id: int
    item_number: int
    name: str
    name_korean: Optional[str] = None
    description: Optional[str] = None
    dietary_info: Optional[str] = None
    price: float
    category_id: int

    class Config:
        orm_mode = True
