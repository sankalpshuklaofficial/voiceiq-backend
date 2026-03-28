from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    business_id: int
    customer_name: str
    customer_phone: Optional[str] = None
    appointment_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    confirmation_sent: Optional[bool] = None

class AppointmentResponse(BaseModel):
    id: int
    business_id: int
    customer_name: str
    customer_phone: Optional[str] = None
    appointment_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: str
    confirmation_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True