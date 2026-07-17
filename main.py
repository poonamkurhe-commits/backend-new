from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database.connection import Database
from routes import auth, questions, results

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting PrepAce API...")
    print(f"📦 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    try:
        await Database.connect()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise
    yield
    # Shutdown
    await Database.disconnect()
    print("🛑 PrepAce API shut down")

app = FastAPI(
    title="PrepAce API",
    version="1.0.0",
    description="Exam Preparation Platform API",
    lifespan=lifespan
)

# CORS middleware - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        os.getenv("FRONTEND_URL", "*")  # Allow custom frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(results.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to PrepAce API",
        "status": "running",
        "version": "1.0.0",
        "database": "MongoDB Atlas",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db = Database.get_collection("users")
        await db.find_one({})
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }