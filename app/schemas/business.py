from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class BusinessCreate(BaseModel):
    name: str
    type_id: int
    phone_number: Optional[str] = None
    address: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = {}

class BusinessResponse(BaseModel):
    id: int
    name: str
    type_id: int
    phone_number: Optional[str] = None
    address: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = {}
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True