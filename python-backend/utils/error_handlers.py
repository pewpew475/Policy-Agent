"""
Error handling utilities and custom exceptions
"""

from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

class InsuranceAIException(Exception):
    """Base exception for Insurance AI application"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentProcessingError(InsuranceAIException):
    """Exception for document processing errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", details)

class AIServiceError(InsuranceAIException):
    """Exception for AI service errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AI_SERVICE_ERROR", details)

class APIKeyError(InsuranceAIException):
    """Exception for API key related errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "API_KEY_ERROR", details)

class RateLimitError(InsuranceAIException):
    """Exception for rate limiting errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)

class ValidationError(InsuranceAIException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

def create_error_response(
    error: Exception,
    status_code: int = 500,
    include_details: bool = False
) -> JSONResponse:
    """Create standardized error response"""
    
    error_data = {
        "error": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    # Add error code if it's our custom exception
    if isinstance(error, InsuranceAIException):
        error_data["error_code"] = error.error_code
        if include_details and error.details:
            error_data["details"] = error.details
    
    # Log the error
    logger.error(f"Error {status_code}: {error_data}")
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def document_processing_error_handler(request: Request, exc: DocumentProcessingError):
    """Handle document processing errors"""
    return create_error_response(exc, 422, include_details=True)

async def ai_service_error_handler(request: Request, exc: AIServiceError):
    """Handle AI service errors"""
    return create_error_response(exc, 503, include_details=True)

async def api_key_error_handler(request: Request, exc: APIKeyError):
    """Handle API key errors"""
    return create_error_response(exc, 401, include_details=False)

async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    """Handle rate limit errors"""
    return create_error_response(exc, 429, include_details=True)

async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    return create_error_response(exc, 400, include_details=True)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    error_data = {
        "error": "HTTPException",
        "message": exc.detail,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_data
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    error_data = {
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(
        status_code=500,
        content=error_data
    )

# Error handler registry
ERROR_HANDLERS = {
    DocumentProcessingError: document_processing_error_handler,
    AIServiceError: ai_service_error_handler,
    APIKeyError: api_key_error_handler,
    RateLimitError: rate_limit_error_handler,
    ValidationError: validation_error_handler,
    HTTPException: http_exception_handler,
    Exception: general_exception_handler
}

def setup_error_handlers(app):
    """Setup error handlers for FastAPI app"""
    
    for exception_type, handler in ERROR_HANDLERS.items():
        app.add_exception_handler(exception_type, handler)
    
    logger.info("Error handlers configured")

# Utility functions for common error scenarios
def validate_file_upload(file, max_size: int = 50 * 1024 * 1024):
    """Validate file upload"""
    
    if not file.filename:
        raise ValidationError("No file provided")
    
    if file.size and file.size > max_size:
        raise ValidationError(
            f"File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB",
            details={"file_size": file.size, "max_size": max_size}
        )
    
    # Check file extension
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif', '.docx', '.doc', '.txt']
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    if f'.{file_extension}' not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file type: {file_extension}",
            details={"allowed_extensions": allowed_extensions}
        )

def validate_api_key_request(request_data: Dict[str, Any]):
    """Validate API key generation request"""
    
    if not request_data.get("name"):
        raise ValidationError("API key name is required")
    
    if len(request_data["name"]) < 3:
        raise ValidationError("API key name must be at least 3 characters")
    
    if request_data.get("rate_limit") and request_data["rate_limit"] < 1:
        raise ValidationError("Rate limit must be at least 1")

def handle_ai_service_timeout():
    """Handle AI service timeout"""
    raise AIServiceError(
        "AI service request timed out",
        details={"timeout": "30 seconds", "suggestion": "Try again later"}
    )

def handle_document_processing_failure(error_details: str):
    """Handle document processing failure"""
    raise DocumentProcessingError(
        "Failed to process document",
        details={"error": error_details, "suggestion": "Check file format and try again"}
    )
