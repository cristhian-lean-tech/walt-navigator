from fastapi import FastAPI, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

from app.api.endpoints import faqs, assistant, agents
from app.core.config import settings
from app.config.init_db import load_faqs, load_paths
from app.services.langchain import CompanyChatbotService

api_key_header = APIKeyHeader(name="Authorization-X", auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_faqs()
    load_paths()
    
    # Start background tasks for session cleanup
    from app.services.background_tasks import start_background_tasks, stop_background_tasks
    start_background_tasks()
    print("✅ Background tasks started (session cleanup)")
    
    yield
    
    # Shutdown
    stop_background_tasks()
    print("✅ Background tasks stopped")    

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION, 
    lifespan=lifespan,    
    openapi_tags=[
        {
            "name": "faqs",
            "description": "FAQ endpoints that require authentication",
        },
    ],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="API documentation with authentication",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "Authorization-X": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization-X",
            "description": "Enter your authentication token"
        }
    }
    
    # Aplicar seguridad a todos los endpoints excepto los públicos
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
    for path, methods in openapi_schema["paths"].items():
        if path not in public_paths:
            for method in methods.values():
                if isinstance(method, dict) and "security" not in method:
                    method["security"] = [{"Authorization-X": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# available cors from any origin
origins = [
    "*",
]
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth import AuthMiddleware

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
app.include_router(faqs.router, prefix="/faqs", tags=["faqs"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
CompanyChatbotService()

@app.get("/")
def read_root():
    return {"message": "Welcome to walt!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}