from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    caller_number = Column(String, nullable=True)
    caller_name = Column(String, nullable=True)
    language = Column(String, default="en")
    intent = Column(String, nullable=True)
    status = Column(String, default="completed")
    duration_seconds = Column(Float, default=0)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    recording_url = Column(String, nullable=True)
    action_taken = Column(String, nullable=True)
    call_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", backref="calls")