from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.api.auth import router as auth_router
from app.config import setting
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code here
    create_db_and_tables()
    yield
    # shutdown code here (nothing needed yet)

app = FastAPI(
    title="Jobpilot",
    description="Backend service for tracking job applications",
    version="1.0.0",
    lifespan=lifespan
)



# 1. Enable CORS (Cross-Origin Resource Sharing) for  frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # NOTE_TO_SELF: TEMPORARY CORS 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)

# 2. Basic root route
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Job Tracker API Backend!",
        "docs_url": "/docs"
    }

# 3. Health check route to verify configuration is working
@app.get("/health")
def health_check():
    # Masking the secret key for security display
    masked_key = setting.SECRET_KEY[:4] + "*" * (len(setting.SECRET_KEY) - 4) if setting.SECRET_KEY else "Missing"
    
    return {
        "status": "healthy",
        "database_configured": bool(setting.DATABASE_URL),
        "secret_key_loaded": bool(masked_key)
    }





