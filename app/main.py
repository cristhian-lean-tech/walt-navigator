from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

from app.api.endpoints import faqs
from app.core.config import settings
from app.config.init_db import load_faqs, load_paths
from app.services.langchain import CompanyChatbotService

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_faqs()
    load_paths()    
    yield    

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# available cors from any origin
origins = [
    "*",
]
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
app.include_router(faqs.router, prefix="/faqs", tags=["faqs"])

CompanyChatbotService()

@app.get("/")
def read_root():
    return {"message": "Welcome to walt!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

