from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth
from app.api.routes import webhooks
from app.api.routes import appointments
from app.api.routes import calls
from app.api.routes import business
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI Voice Receptionist SaaS Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(webhooks.router)
app.include_router(appointments.router)
app.include_router(calls.router)
app.include_router(business.router)

@app.get("/")
def root():
    return {"message": "VoiceIQ API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}