from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "VoiceIQ"
    SECRET_KEY: str = "changethisinsecretkeyinproduction"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/voiceiq"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    OPENAI_API_KEY: str = ""
    DEEPGRAM_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "ap-south-1"
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
