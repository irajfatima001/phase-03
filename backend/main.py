from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.database.session import engine
from src.api.auth import router as auth_router
from src.api.v1.conversations import router as conversations_router
from src.api.v1.tasks import router as v1_tasks_router
from src.core.config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    try:
        # Use the sync engine directly
        SQLModel.metadata.create_all(bind=engine)
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise
    yield
    # Cleanup on shutdown


app = FastAPI(
    title="AI Todo Chatbot API",
    description="Backend API for the AI-powered Todo app with chatbot integration",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS.split(",") if settings.BACKEND_CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose authorization header to frontend
    expose_headers=["Authorization"]
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(v1_tasks_router, prefix="/api/v1", tags=["tasks"])
app.include_router(conversations_router, prefix="/api/v1", tags=["conversations"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Todo Chatbot API", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Todo Chatbot API"}