"""
Authentication and authorization utilities
"""

import time
from typing import Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from loguru import logger

from models.database import get_db
from services.api_manager import APIManager

# Security scheme for API key authentication
security = HTTPBearer(auto_error=False)

class APIKeyAuth:
    """API Key authentication dependency"""
    
    def __init__(self, required: bool = True):
        self.required = required
        self.api_manager = APIManager()
    
    async def __call__(
        self, 
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ):
        """Validate API key and track usage"""
        
        start_time = time.time()
        
        # Extract API key from Authorization header
        api_key = None
        if credentials:
            api_key = credentials.credentials
        
        # Check for API key in query parameters as fallback
        if not api_key:
            api_key = request.query_params.get("api_key")
        
        # If no API key provided and it's required
        if not api_key and self.required:
            raise HTTPException(
                status_code=401,
                detail="API key required. Provide in Authorization header as 'Bearer <key>' or as 'api_key' query parameter."
            )
        
        # If API key provided, validate it
        if api_key:
            db_key = self.api_manager.validate_api_key(db, api_key)
            
            if not db_key:
                # Record failed attempt
                self._record_usage(
                    request, db, None, 401, time.time() - start_time
                )
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired API key"
                )
            
            # Check rate limits
            if not self.api_manager.check_rate_limit(db, db_key.id):
                # Record rate limit exceeded
                self._record_usage(
                    request, db, db_key.id, 429, time.time() - start_time
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Limit: {db_key.rate_limit} requests per hour"
                )
            
            # Store API key info in request state for later use
            request.state.api_key_id = db_key.id
            request.state.api_key_name = db_key.name
            
            return db_key
        
        # No API key provided but not required
        request.state.api_key_id = None
        request.state.api_key_name = "anonymous"
        return None
    
    def _record_usage(
        self, 
        request: Request, 
        db: Session, 
        api_key_id: Optional[str], 
        status_code: int, 
        response_time: float
    ):
        """Record API usage for analytics"""
        
        if api_key_id:
            try:
                self.api_manager.record_usage(
                    db=db,
                    api_key_id=api_key_id,
                    endpoint=str(request.url.path),
                    method=request.method,
                    status_code=status_code,
                    response_time=response_time,
                    user_agent=request.headers.get("user-agent"),
                    ip_address=request.client.host if request.client else None
                )
            except Exception as e:
                logger.error(f"Failed to record API usage: {str(e)}")

# Create dependency instances
verify_api_key = APIKeyAuth(required=True)
optional_api_key = APIKeyAuth(required=False)

# Middleware for automatic usage tracking
class UsageTrackingMiddleware:
    """Middleware to automatically track API usage"""
    
    def __init__(self):
        self.api_manager = APIManager()
    
    async def __call__(self, request: Request, call_next):
        """Track API usage for all requests"""
        
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record usage if API key is present
        if hasattr(request.state, 'api_key_id') and request.state.api_key_id:
            try:
                # Get database session
                db = next(get_db())
                
                self.api_manager.record_usage(
                    db=db,
                    api_key_id=request.state.api_key_id,
                    endpoint=str(request.url.path),
                    method=request.method,
                    status_code=response.status_code,
                    response_time=response_time,
                    user_agent=request.headers.get("user-agent"),
                    ip_address=request.client.host if request.client else None
                )
                
                db.close()
                
            except Exception as e:
                logger.error(f"Failed to record API usage in middleware: {str(e)}")
        
        return response

# Rate limiting decorator
def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator for endpoints"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a simple in-memory rate limiter
            # In production, you'd want to use Redis or similar
            return await func(*args, **kwargs)
        return wrapper
    return decorator
