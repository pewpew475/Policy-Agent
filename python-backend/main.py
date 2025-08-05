"""
Insurance AI Assistant FastAPI Backend
Main application entry point with comprehensive document processing and AI integration
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uvicorn
import httpx
from dotenv import load_dotenv
from loguru import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import our custom modules
from services.document_processor import DocumentProcessor
from services.ai_service import AIService
from services.api_manager import APIManager
from services.analytics_service import AnalyticsService
from models.database import init_db, get_db
from models.schemas import (
    DocumentUploadResponse,
    ChatMessage,
    ChatResponse,
    ChatRequest,
    APIKeyRequest,
    APIKeyResponse,
    AnalyticsResponse,
    HackathonRequest,
    HackathonResponse,
    ProcessingStatus,
    MessageRole
)
from utils.auth import verify_api_key
from utils.config import settings

# Load environment variables
load_dotenv()

# Configure logging
logger.add("logs/app.log", rotation="1 day", retention="30 days", level="INFO")

# Security setup
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Insurance AI Backend...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    app.state.document_processor = DocumentProcessor()
    app.state.ai_service = AIService()
    app.state.api_manager = APIManager()
    app.state.analytics_service = AnalyticsService()
    
    # Create upload directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed_documents", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("✅ Backend initialization complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Insurance AI Backend...")

# Create FastAPI app
app = FastAPI(
    title="Insurance AI Assistant API",
    description="Comprehensive AI-powered insurance document processing and chat assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error in {request.method} {request.url}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat()
            }
        )

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request, call_next):
    """Request logging middleware"""
    start_time = time.time()

    # Log request
    logger.info(f"📥 {request.method} {request.url}")

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")

    return response

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "document_processor": "active",
            "ai_service": "active",
            "api_manager": "active",
            "analytics": "active"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Insurance AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# DOCUMENT PROCESSING ENDPOINTS
# ============================================================================

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process insurance document"""

    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )

    # Read file content
    file_content = await file.read()

    # Process document
    result = await app.state.document_processor.process_upload(
        file_content, file.filename, file.content_type
    )

    if result["processing_status"] == ProcessingStatus.FAILED:
        raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))

    # Generate summary using AI
    if result.get("extracted_text"):
        summary_result = await app.state.ai_service.generate_summary(
            result["extracted_text"],
            result["document_type"]
        )
        result.update(summary_result)

    # Save to database
    from models.database import create_document_record, update_document_processing

    document = create_document_record(
        db=db,
        document_id=result["document_id"],
        filename=result["filename"],
        original_filename=result["original_filename"],
        file_path=result["file_path"],
        file_size=result["file_size"],
        document_type=result["document_type"]
    )

    if result.get("extracted_text"):
        update_document_processing(
            db=db,
            document_id=result["document_id"],
            extracted_text=result["extracted_text"],
            summary=result.get("summary", ""),
            key_points=result.get("key_points", []),
            page_count=result.get("page_count"),
            confidence_score=result.get("confidence_score")
        )

    return DocumentUploadResponse(**result, upload_timestamp=document.upload_timestamp)

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document information"""

    from models.database import Document
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document.id,
        "filename": document.original_filename,
        "document_type": document.document_type,
        "processing_status": document.processing_status,
        "summary": document.summary,
        "key_points": document.key_points,
        "page_count": document.page_count,
        "upload_timestamp": document.upload_timestamp,
        "processed_timestamp": document.processed_timestamp
    }

@app.get("/api/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List uploaded documents"""

    from models.database import Document
    documents = db.query(Document).offset(skip).limit(limit).all()

    return [
        {
            "document_id": doc.id,
            "filename": doc.original_filename,
            "document_type": doc.document_type,
            "processing_status": doc.processing_status,
            "upload_timestamp": doc.upload_timestamp
        }
        for doc in documents
    ]

# ============================================================================
# CHAT AND AI ENDPOINTS
# ============================================================================

@app.post("/api/chat")
async def chat_completion(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with AI assistant"""

    # Get document context if document IDs provided
    document_context = None
    if request.document_ids:
        from models.database import Document
        documents = db.query(Document).filter(
            Document.id.in_(request.document_ids)
        ).all()

        context_parts = []
        for doc in documents:
            if doc.extracted_text:
                context_parts.append(f"Document: {doc.original_filename}\n{doc.extracted_text[:2000]}...")

        document_context = "\n\n".join(context_parts)

    # Prepare messages
    messages = [ChatMessage(role=MessageRole.USER, content=request.message)]

    # Generate response
    if request.stream:
        async def generate():
            async for chunk in app.state.ai_service.chat_completion(
                messages=messages,
                document_context=document_context,
                use_groq=True,
                stream=True
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/plain")
    else:
        # Non-streaming response
        response_content = ""
        async for chunk in app.state.ai_service.chat_completion(
            messages=messages,
            document_context=document_context,
            use_groq=True,
            stream=False
        ):
            response_content += chunk

        return ChatResponse(
            message=response_content,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            response_time=0.5,  # Placeholder
            sources=request.document_ids
        )

# ============================================================================
# API MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/keys/generate", response_model=APIKeyResponse)
async def generate_api_key(
    request: APIKeyRequest,
    db: Session = Depends(get_db)
):
    """Generate a new API key"""

    return app.state.api_manager.generate_api_key(db, request)

@app.get("/api/keys")
async def list_api_keys(db: Session = Depends(get_db)):
    """List all API keys (without the actual keys)"""

    return app.state.api_manager.get_api_keys(db)

@app.put("/api/keys/{key_id}/deactivate")
async def deactivate_api_key(key_id: str, db: Session = Depends(get_db)):
    """Deactivate an API key"""

    success = app.state.api_manager.deactivate_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key deactivated successfully"}

@app.put("/api/keys/{key_id}/activate")
async def activate_api_key(key_id: str, db: Session = Depends(get_db)):
    """Reactivate an API key"""

    success = app.state.api_manager.reactivate_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key activated successfully"}

@app.get("/api/keys/{key_id}/stats")
async def get_api_key_stats(
    key_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get usage statistics for an API key"""

    return app.state.api_manager.get_usage_stats(db, key_id, days)

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get analytics data for dashboard"""

    return app.state.analytics_service.get_dashboard_analytics(db, days)

@app.get("/api/analytics/health")
async def get_system_health(db: Session = Depends(get_db)):
    """Get system health metrics"""

    return app.state.analytics_service.get_system_health(db)

@app.get("/api/analytics/api-keys")
async def get_api_key_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get analytics per API key"""

    return app.state.analytics_service.get_api_key_analytics(db, days)

# ============================================================================
# FRONTEND INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/frontend/upload")
async def frontend_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Handle file upload from frontend - extract text and store, no AI processing yet"""

    uploaded_documents = []

    # Process uploaded files
    for file in files:
        if file.filename and file.filename.strip():
            try:
                # Process file upload
                file_content = await file.read()
                result = await app.state.document_processor.process_upload(
                    file_content, file.filename, file.content_type
                )

                if result["processing_status"] != ProcessingStatus.FAILED:
                    # Save to database
                    from models.database import create_document_record, update_document_processing

                    document = create_document_record(
                        db=db,
                        document_id=result["document_id"],
                        filename=result["filename"],
                        original_filename=result["original_filename"],
                        file_path=result["file_path"],
                        file_size=result["file_size"],
                        document_type=result["document_type"]
                    )

                    # Store extracted text without AI processing
                    if result.get("extracted_text"):
                        update_document_processing(
                            db=db,
                            document_id=result["document_id"],
                            extracted_text=result["extracted_text"],
                            summary="Text extracted - ready for AI analysis",
                            key_points=[],
                            page_count=result.get("page_count"),
                            confidence_score=result.get("confidence_score")
                        )

                    uploaded_documents.append({
                        "document_id": result["document_id"],
                        "filename": result["original_filename"],
                        "status": "ready",
                        "text_length": len(result.get("extracted_text", "")),
                        "page_count": result.get("page_count")
                    })
                else:
                    uploaded_documents.append({
                        "filename": file.filename,
                        "status": "failed",
                        "error": result.get("error", "Processing failed")
                    })

            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                uploaded_documents.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })

    return {"uploaded_documents": uploaded_documents}

@app.post("/api/frontend/chat")
async def frontend_chat(
    message: str = Form(...),
    document_ids: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """Handle chat message from frontend - AI processes stored documents"""

    # Parse document IDs
    doc_ids = []
    if document_ids.strip():
        doc_ids = [id.strip() for id in document_ids.split(",") if id.strip()]

    # Get document context from stored documents
    document_context = None
    if doc_ids:
        from models.database import Document
        documents = db.query(Document).filter(
            Document.id.in_(doc_ids)
        ).all()

        context_parts = []
        for doc in documents:
            if doc.extracted_text:
                context_parts.append(f"Document: {doc.original_filename}\n{doc.extracted_text}")

        document_context = "\n\n".join(context_parts)

    # Generate AI response using GLM-4.5-FLASH
    messages = [ChatMessage(role=MessageRole.USER, content=message)]

    async def generate():
        async for chunk in app.state.ai_service.chat_completion(
            messages=messages,
            document_context=document_context,
            stream=True
        ):
            yield f"data: {json.dumps({'content': chunk, 'document_ids': doc_ids})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/hackrx/run", response_model=HackathonResponse)
async def hackathon_evaluation(
    request: HackathonRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    HACKATHON EVALUATION ENDPOINT

    This is the main evaluation endpoint for the hackathon.
    Downloads document from URL, processes it, and answers all questions.
    """

    # Verify API key
    api_key = credentials.credentials
    if not verify_api_key(api_key, db):
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Step 1: Download document from URL
        logger.info(f"🏆 HACKATHON: Downloading document from {request.documents}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(request.documents)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download document: {response.status_code}")

            document_content = response.content

        # Step 2: Process the document
        logger.info("🏆 HACKATHON: Processing document...")

        # Extract filename from URL
        filename = request.documents.split('/')[-1].split('?')[0]
        if not filename.endswith(('.pdf', '.txt', '.docx')):
            filename += '.pdf'  # Default to PDF

        # Process the document
        result = await app.state.document_processor.process_upload(
            document_content, filename, "application/pdf"
        )

        if result["processing_status"] == ProcessingStatus.FAILED:
            raise HTTPException(status_code=500, detail="Document processing failed")

        document_text = result.get("extracted_text", "")
        if not document_text:
            raise HTTPException(status_code=500, detail="No text extracted from document")

        logger.info(f"🏆 HACKATHON: Document processed, {len(document_text)} characters extracted")

        # Step 3: Answer all questions using AI
        answers = []

        for i, question in enumerate(request.questions):
            logger.info(f"🏆 HACKATHON: Processing question {i+1}/{len(request.questions)}: {question[:50]}...")

            try:
                # Use AI service to answer the question
                messages = [ChatMessage(role=MessageRole.USER, content=question)]

                # Collect the full response
                full_response = ""
                async for chunk in app.state.ai_service.chat_completion(
                    messages=messages,
                    document_context=document_text,
                    stream=True
                ):
                    full_response += chunk

                answers.append(full_response.strip())
                logger.info(f"🏆 HACKATHON: Question {i+1} answered: {full_response[:100]}...")

            except Exception as e:
                logger.error(f"🏆 HACKATHON: Error answering question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")

        logger.info(f"🏆 HACKATHON: All {len(request.questions)} questions processed successfully")

        return HackathonResponse(answers=answers)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🏆 HACKATHON: Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"🚀 Starting Insurance AI Backend on {host}:{port}")
    logger.info(f"📊 Debug mode: {debug}")
    logger.info(f"🔑 GLM API Key: {'✓ Set' if os.getenv('GLM_API_KEY') else '✗ Missing'}")
    logger.info(f"🌐 GLM API URL: {os.getenv('GLM_API_URL', 'Not set')}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
