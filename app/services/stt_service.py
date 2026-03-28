import openai
from app.core.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(audio_file_path: str, language: str = None) -> dict:
    """
    Convert speech audio file to text using OpenAI Whisper
    Returns transcript and detected language
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
        return {
            "text": transcript.text,
            "language": transcript.language,
            "success": True
        }
    except Exception as e:
        print(f"STT Error: {e}")
        return {
            "text": "",
            "language": "en",
            "success": False,
            "error": str(e)
        }

async def transcribe_from_url(audio_url: str) -> dict:
    """
    Download audio from URL and transcribe it
    Used for Twilio recordings
    """
    import httpx
    import tempfile
    import os

    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(audio_url)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".wav"
            ) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

        result = await transcribe_audio(tmp_path)
        os.unlink(tmp_path)
        return result

    except Exception as e:
        print(f"STT URL Error: {e}")
        return {
            "text": "",
            "language": "en",
            "success": False,
            "error": str(e)
        }