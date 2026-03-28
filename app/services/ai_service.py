from groq import Groq
from app.core.config import settings
from app.prompts.hospital import HOSPITAL_PROMPT
from app.prompts.hotel import HOTEL_PROMPT
from app.prompts.real_estate import REAL_ESTATE_PROMPT
from app.prompts.restaurant import RESTAURANT_PROMPT

client = Groq(api_key=settings.GROQ_API_KEY)

PROMPT_MAP = {
    "hospital": HOSPITAL_PROMPT,
    "hotel": HOTEL_PROMPT,
    "real_estate": REAL_ESTATE_PROMPT,
    "restaurant": RESTAURANT_PROMPT,
}

async def get_ai_response(
    user_message: str,
    business_type: str,
    business_name: str,
    knowledge_base: dict,
    conversation_history: list,
    language: str = "en"
) -> dict:
    try:
        system_prompt = PROMPT_MAP.get(
            business_type, HOSPITAL_PROMPT
        ).format(
            business_name=business_name,
            knowledge_base=str(knowledge_base),
            language=language
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        ai_text = response.choices[0].message.content
        intent = detect_intent(user_message)

        return {
            "response": ai_text,
            "intent": intent,
            "success": True
        }

    except Exception as e:
        print(f"AI Service Error: {e}")
        return {
            "response": "I apologize, I am having trouble understanding. Please call back.",
            "intent": "error",
            "success": False
        }

def detect_intent(message: str) -> str:
    message_lower = message.lower()

    appointment_keywords = [
        "appointment", "book", "schedule", "doctor",
        "appoint", "मिलना", "अपॉइंटमेंट", "बुक"
    ]
    enquiry_keywords = [
        "price", "cost", "timing", "hours", "information",
        "जानकारी", "कीमत", "समय"
    ]
    booking_keywords = [
        "room", "hotel", "stay", "check in", "reserve",
        "कमरा", "बुकिंग"
    ]
    emergency_keywords = [
        "emergency", "urgent", "immediately",
        "इमरजेंसी", "जरूरी"
    ]

    if any(k in message_lower for k in emergency_keywords):
        return "emergency"
    elif any(k in message_lower for k in appointment_keywords):
        return "appointment"
    elif any(k in message_lower for k in booking_keywords):
        return "booking"
    elif any(k in message_lower for k in enquiry_keywords):
        return "enquiry"
    else:
        return "general"