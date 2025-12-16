"""
Authentication middleware for validating API tokens.

This middleware checks for a valid AUTH_TOKEN in the request headers.
If the token is missing or invalid, it returns a 401 Unauthorized response.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
import os
import logging

logger = logging.getLogger(__name__)

# Get AUTH_TOKEN from environment
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate authentication token in request headers.
    
    Expected header:
        Authorization-X: <token>
    """
    
    # Endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request and validate authentication.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            Response from the endpoint or 401 error
        """
        # Check if path is public (no auth required)
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # Check if AUTH_TOKEN is configured
        if not AUTH_TOKEN:
            logger.warning("[AUTH] AUTH_TOKEN not configured in environment")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "Authentication not configured"
                }
            )
        
        # Extract token from headers
        token = self._extract_token(request)
        
        # Validate token
        if not token:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Authentication token is required"
                }
            )
        
        if token != AUTH_TOKEN:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid authentication token"
                }
            )
        
        # Token is valid, proceed with request
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        return path in self.PUBLIC_PATHS
    
    def _extract_token(self, request: Request) -> str | None:
        # Try Authorization-X header
        token_header = request.headers.get("Authorization-X")
        if token_header:
            return token_header
        
        return None

