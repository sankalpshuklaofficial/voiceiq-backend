from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    appointment_type = Column(String, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default="pending")
    confirmation_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", backref="appointments")
    call = relationship("Call", backref="appointment")