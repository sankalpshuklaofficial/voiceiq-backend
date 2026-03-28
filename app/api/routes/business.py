from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.business import Business, BusinessType
from app.schemas.business import BusinessCreate, BusinessResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/business", tags=["Business"])

@router.get("/types")
def get_business_types(db: Session = Depends(get_db)):
    types = db.query(BusinessType).all()
    if not types:
        defaults = [
            BusinessType(type_key="hospital", label="Hospital / Clinic"),
            BusinessType(type_key="hotel", label="Hotel / Resort"),
            BusinessType(type_key="real_estate", label="Real Estate Agency"),
            BusinessType(type_key="restaurant", label="Restaurant"),
        ]
        for t in defaults:
            db.add(t)
        db.commit()
        types = db.query(BusinessType).all()
    return types

@router.post("/", response_model=BusinessResponse)
def create_business(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = Business(**data.model_dump(), owner_id=current_user.id)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business

@router.get("/", response_model=List[BusinessResponse])
def get_my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Business).filter(
        Business.owner_id == current_user.id
    ).all()

@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user.id
    ).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.patch("/{business_id}", response_model=BusinessResponse)
def update_business(
    business_id: int,
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_id == current_user.id
    ).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business