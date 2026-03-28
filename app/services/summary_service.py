import openai
from app.core.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_call_summary(
    transcript: str,
    business_type: str,
    business_name: str
) -> dict:
    """
    Generate structured summary after call ends
    Returns caller name, intent, key details, action taken
    """
    try:
        prompt = f"""
        Analyze this phone call transcript for {business_name} ({business_type}).
        
        Transcript:
        {transcript}
        
        Generate a structured summary with these exact fields:
        - caller_name: (name of the caller if mentioned, else "Unknown")
        - intent: (main purpose: appointment/enquiry/booking/complaint/general)
        - key_details: (important information collected)
        - action_taken: (what was done or promised)
        - follow_up_required: (yes/no)
        - language_used: (English/Hindi/Mixed)
        
        Respond in JSON format only.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a call center analyst. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        import json
        summary_text = response.choices[0].message.content
        summary_text = summary_text.replace("```json", "").replace("```", "").strip()
        summary = json.loads(summary_text)
        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        print(f"Summary Error: {e}")
        return {
            "success": False,
            "summary": {
                "caller_name": "Unknown",
                "intent": "general",
                "key_details": "Could not generate summary",
                "action_taken": "None",
                "follow_up_required": "no",
                "language_used": "Unknown"
            }
        }


def format_summary_for_display(summary: dict) -> str:
    """
    Format summary dict into readable text
    """
    s = summary.get("summary", {})
    return f"""
📞 CALL SUMMARY
━━━━━━━━━━━━━━━━━━━━
👤 Caller: {s.get('caller_name', 'Unknown')}
🎯 Intent: {s.get('intent', 'general')}
📝 Key Details: {s.get('key_details', 'N/A')}
✅ Action Taken: {s.get('action_taken', 'None')}
🔄 Follow Up: {s.get('follow_up_required', 'no')}
🌐 Language: {s.get('language_used', 'Unknown')}
━━━━━━━━━━━━━━━━━━━━
    """.strip()