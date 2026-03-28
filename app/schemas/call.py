from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class CallResponse(BaseModel):
    id: int
    business_id: int
    caller_number: Optional[str] = None
    caller_name: Optional[str] = None
    language: Optional[str] = None
    intent: Optional[str] = None
    status: str
    duration_seconds: Optional[float] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    action_taken: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CallSummaryResponse(BaseModel):
    call_id: int
    caller_name: str
    intent: str
    key_details: str
    action_taken: str
    follow_up_required: str
    language_used: str