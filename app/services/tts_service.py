import openai
from app.core.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

async def text_to_speech(
    text: str,
    voice: str = "alloy",
    language: str = "en"
) -> bytes:
    """
    Convert text to speech using OpenAI TTS
    Returns audio bytes
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def get_voice_for_language(language: str) -> str:
    """
    Select appropriate voice based on language
    """
    voice_map = {
        "hi": "alloy",
        "en": "nova",
        "te": "alloy",
        "ta": "alloy",
        "mr": "alloy",
        "gu": "alloy",
        "bn": "alloy",
    }
    return voice_map.get(language, "nova")