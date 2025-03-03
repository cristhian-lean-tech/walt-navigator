from fastapi import FastAPI
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

load_dotenv()

from app.api.endpoints import assistant
from app.core.config import settings
from app.services.navigation import NavigationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    navigation_service = NavigationService()
    navigation_service.init_database()
    print("Database initialized")
    yield
    # Clean up the Vector DB
    print("Cleaning up the database")
    navigation_service.cleanup_database()
    

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

app.include_router(assistant.router, prefix="/assistant", tags=["assistant"])

@app.get("/")
def read_root():
    return {"message": "Welcome to walt!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

