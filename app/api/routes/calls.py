from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.call import Call
from app.schemas.call import CallResponse
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.summary_service import generate_call_summary

router = APIRouter(prefix="/api/calls", tags=["Calls"])

@router.get("/", response_model=List[CallResponse])
def get_calls(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Call).filter(
        Call.business_id == business_id
    ).order_by(Call.created_at.desc()).all()

@router.get("/{call_id}", response_model=CallResponse)
def get_call(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@router.post("/{call_id}/summarize")
async def summarize_call(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    if not call.transcript:
        raise HTTPException(
            status_code=400,
            detail="No transcript available"
        )
    business = call.business
    result = await generate_call_summary(
        transcript=call.transcript,
        business_type=business.business_type.type_key,
        business_name=business.name
    )
    if result["success"]:
        import json
        call.summary = json.dumps(result["summary"])
        db.commit()
    return result

@router.get("/analytics/overview")
def get_analytics(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_calls = db.query(Call).filter(
        Call.business_id == business_id
    ).count()

    completed = db.query(Call).filter(
        Call.business_id == business_id,
        Call.status == "completed"
    ).count()

    intents = {}
    calls = db.query(Call).filter(
        Call.business_id == business_id
    ).all()

    for call in calls:
        intent = call.intent or "general"
        intents[intent] = intents.get(intent, 0) + 1

    return {
        "total_calls": total_calls,
        "completed_calls": completed,
        "intent_breakdown": intents
    }