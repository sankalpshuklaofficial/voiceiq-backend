from fastapi import APIRouter, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.business import Business, BusinessType
from app.models.call import Call
from app.services.ai_service import get_ai_response, detect_intent
import json

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# Store conversation sessions in memory
conversation_sessions = {}

@router.post("/voice/incoming")
async def incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
):
    """
    Handle incoming Twilio call
    This endpoint is called when someone calls your Twilio number
    """
    db = SessionLocal()
    try:
        print(f"DEBUG - To: {repr(To)}, From: {repr(From)}")
        all_businesses = db.query(Business).all()
        for b in all_businesses:
            print(f"DEBUG - Business: {b.name}, Phone: {repr(b.phone_number)}")
        business = db.query(Business).filter(
            Business.phone_number == To
        ).first()
        print(f"DEBUG - Business found: {business}")

        if not business:
            response = VoiceResponse()
            response.say(
                "Sorry, this number is not configured. Goodbye.",
                voice="Polly.Aditi"
            )
            response.hangup()
            return Response(
                content=str(response),
                media_type="application/xml"
            )

        business_type = business.business_type.type_key
        knowledge_base = business.profile_data or {}

        conversation_sessions[CallSid] = {
            "business_id": business.id,
            "business_type": business_type,
            "business_name": business.name,
            "knowledge_base": knowledge_base,
            "history": [],
            "caller_number": From,
            "language": "en"
        }

        new_call = Call(
            business_id=business.id,
            caller_number=From,
            status="in_progress"
        )
        db.add(new_call)
        db.commit()
        db.refresh(new_call)
        conversation_sessions[CallSid]["call_id"] = new_call.id

        greeting = get_greeting(business.name, business_type)

        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action=f"/webhook/voice/respond?CallSid={CallSid}",
            method="POST",
            language="hi-IN",
            speech_timeout="auto",
            timeout=5
        )
        gather.say(greeting, voice="Polly.Aditi")
        response.append(gather)
        response.say(
            "I did not hear anything. Please call again.",
            voice="Polly.Aditi"
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    finally:
        db.close()


@router.post("/voice/respond")
async def handle_response(
    request: Request,
    CallSid: str = None,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
):
    """
    Handle caller's speech and respond with AI
    """
    if not CallSid:
        params = dict(request.query_params)
        CallSid = params.get("CallSid", "")

    session = conversation_sessions.get(CallSid, {})

    if not session:
        response = VoiceResponse()
        response.say("Session expired. Please call again.")
        response.hangup()
        return Response(
            content=str(response),
            media_type="application/xml"
        )

    caller_message = SpeechResult or ""

    ai_result = await get_ai_response(
        user_message=caller_message,
        business_type=session.get("business_type", "hospital"),
        business_name=session.get("business_name", ""),
        knowledge_base=session.get("knowledge_base", {}),
        conversation_history=session.get("history", []),
        language=session.get("language", "en")
    )

    ai_response_text = ai_result.get("response", "")
    intent = ai_result.get("intent", "general")

    session["history"].append({"role": "user", "content": caller_message})
    session["history"].append({"role": "assistant", "content": ai_response_text})
    session["intent"] = intent

    db = SessionLocal()
    try:
        if "call_id" in session:
            call = db.query(Call).filter(
                Call.id == session["call_id"]
            ).first()
            if call:
                history_text = "\n".join([
                    f"{m['role'].upper()}: {m['content']}"
                    for m in session["history"]
                ])
                call.transcript = history_text
                call.intent = intent
                db.commit()
    finally:
        db.close()

    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=f"/webhook/voice/respond?CallSid={CallSid}",
        method="POST",
        language="hi-IN",
        speech_timeout="auto",
        timeout=5
    )
    gather.say(ai_response_text, voice="Polly.Aditi")
    response.append(gather)
    response.say("Thank you for calling. Goodbye!", voice="Polly.Aditi")
    response.hangup()

    return Response(
        content=str(response),
        media_type="application/xml"
    )


@router.post("/voice/status")
async def call_status(
    request: Request,
    CallSid: str = Form(default=""),
    CallStatus: str = Form(default=""),
    CallDuration: str = Form(default="0"),
):
    """
    Handle call completion and save final data
    """
    db = SessionLocal()
    try:
        session = conversation_sessions.get(CallSid, {})
        if session and "call_id" in session:
            call = db.query(Call).filter(
                Call.id == session["call_id"]
            ).first()
            if call:
                call.status = "completed"
                call.duration_seconds = float(CallDuration or 0)
                db.commit()

        if CallSid in conversation_sessions:
            del conversation_sessions[CallSid]

    finally:
        db.close()

    return {"status": "ok"}


def get_greeting(business_name: str, business_type: str) -> str:
    greetings = {
        "hospital": f"Namaste! Welcome to {business_name}. Main aapki kaise madad kar sakta hoon? You can also speak in English.",
        "hotel": f"Namaste! Welcome to {business_name}. How may I assist you today?",
        "real_estate": f"Namaste! Thank you for calling {business_name}. How can I help you today?",
        "restaurant": f"Namaste! Welcome to {business_name}. How can I assist you today?",
    }
    return greetings.get(
        business_type,
        f"Namaste! Welcome to {business_name}. How can I help you?"
    )