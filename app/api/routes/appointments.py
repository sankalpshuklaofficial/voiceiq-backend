from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.appointment import Appointment
from app.models.business import Business
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.notification_service import send_appointment_confirmation

router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = Appointment(**data.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Appointment).filter(
        Appointment.business_id == business_id
    ).order_by(Appointment.created_at.desc()).all()

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}

@router.post("/{appointment_id}/confirm")
async def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.customer_phone and appointment.scheduled_at:
        business = db.query(Business).filter(
            Business.id == appointment.business_id
        ).first()
        await send_appointment_confirmation(
            customer_phone=appointment.customer_phone,
            customer_name=appointment.customer_name,
            business_name=business.name if business else "Business",
            appointment_time=str(appointment.scheduled_at)
        )
        appointment.confirmation_sent = True
        db.commit()
    return {"message": "Confirmation sent successfully"}