from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class BusinessType(Base):
    __tablename__ = "business_types"

    id = Column(Integer, primary_key=True, index=True)
    type_key = Column(String, unique=True, nullable=False)
    label = Column(String, nullable=False)

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("business_types.id"), nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    profile_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="businesses")
    business_type = relationship("BusinessType")