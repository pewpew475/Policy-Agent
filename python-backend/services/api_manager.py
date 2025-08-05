"""
API Management Service
Handles API key generation, validation, and usage tracking
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from loguru import logger

from models.database import APIKey, APIUsage, get_db
from models.schemas import APIKeyRequest, APIKeyResponse, APIKeyInfo
from utils.config import settings

class APIManager:
    """API key management and validation service"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        logger.info("API Manager initialized")
    
    def generate_api_key(
        self, 
        db: Session, 
        request: APIKeyRequest
    ) -> APIKeyResponse:
        """Generate a new API key"""
        
        # Generate secure API key
        api_key = f"iai_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(api_key)
        key_id = str(uuid.uuid4())
        
        # Create database record
        db_api_key = APIKey(
            id=key_id,
            key_hash=key_hash,
            name=request.name,
            description=request.description,
            rate_limit=request.rate_limit or 1000,
            expires_at=request.expires_at
        )
        
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        logger.info(f"Generated API key: {request.name} ({key_id})")
        
        return APIKeyResponse(
            key_id=key_id,
            api_key=api_key,
            name=request.name,
            description=request.description,
            rate_limit=request.rate_limit or 1000,
            created_at=db_api_key.created_at,
            expires_at=request.expires_at,
            is_active=True
        )
    
    def validate_api_key(self, db: Session, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key info if valid"""
        
        if not api_key or not api_key.startswith("iai_"):
            return None
        
        key_hash = self._hash_key(api_key)
        
        # Find API key in database
        db_key = db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()
        
        if not db_key:
            return None
        
        # Check expiration
        if db_key.expires_at and db_key.expires_at < datetime.utcnow():
            logger.warning(f"API key expired: {db_key.name}")
            return None
        
        # Update last used timestamp
        db_key.last_used = datetime.utcnow()
        db.commit()
        
        return db_key
    
    def check_rate_limit(self, db: Session, api_key_id: str) -> bool:
        """Check if API key is within rate limits"""
        
        # Get API key info
        db_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if not db_key:
            return False
        
        # Check usage in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        usage_count = db.query(APIUsage).filter(
            APIUsage.api_key_id == api_key_id,
            APIUsage.timestamp >= one_hour_ago
        ).count()
        
        return usage_count < db_key.rate_limit
    
    def record_usage(
        self,
        db: Session,
        api_key_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Record API usage for analytics"""
        
        usage_record = APIUsage(
            id=str(uuid.uuid4()),
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(usage_record)
        
        # Update usage count on API key
        db_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if db_key:
            db_key.usage_count += 1
        
        db.commit()
    
    def get_api_keys(self, db: Session) -> List[APIKeyInfo]:
        """Get list of all API keys (without the actual keys)"""
        
        api_keys = db.query(APIKey).all()
        
        result = []
        for key in api_keys:
            # Get recent usage count
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_usage = db.query(APIUsage).filter(
                APIUsage.api_key_id == key.id,
                APIUsage.timestamp >= one_hour_ago
            ).count()
            
            result.append(APIKeyInfo(
                key_id=key.id,
                name=key.name,
                description=key.description,
                rate_limit=key.rate_limit,
                usage_count=key.usage_count,
                created_at=key.created_at,
                expires_at=key.expires_at,
                is_active=key.is_active,
                last_used=key.last_used
            ))
        
        return result
    
    def deactivate_api_key(self, db: Session, key_id: str) -> bool:
        """Deactivate an API key"""
        
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key:
            return False
        
        db_key.is_active = False
        db.commit()
        
        logger.info(f"Deactivated API key: {db_key.name} ({key_id})")
        return True
    
    def reactivate_api_key(self, db: Session, key_id: str) -> bool:
        """Reactivate an API key"""
        
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key:
            return False
        
        db_key.is_active = True
        db.commit()
        
        logger.info(f"Reactivated API key: {db_key.name} ({key_id})")
        return True
    
    def update_rate_limit(self, db: Session, key_id: str, new_limit: int) -> bool:
        """Update rate limit for an API key"""
        
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key:
            return False
        
        old_limit = db_key.rate_limit
        db_key.rate_limit = new_limit
        db.commit()
        
        logger.info(f"Updated rate limit for {db_key.name}: {old_limit} -> {new_limit}")
        return True
    
    def get_usage_stats(self, db: Session, key_id: str, days: int = 7) -> Dict:
        """Get usage statistics for an API key"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        usage_records = db.query(APIUsage).filter(
            APIUsage.api_key_id == key_id,
            APIUsage.timestamp >= start_date
        ).all()
        
        total_requests = len(usage_records)
        successful_requests = len([r for r in usage_records if 200 <= r.status_code < 300])
        failed_requests = total_requests - successful_requests
        
        avg_response_time = 0
        if usage_records:
            avg_response_time = sum(r.response_time for r in usage_records) / len(usage_records)
        
        # Group by endpoint
        endpoint_stats = {}
        for record in usage_records:
            endpoint = record.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"count": 0, "avg_time": 0}
            endpoint_stats[endpoint]["count"] += 1
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "average_response_time": avg_response_time,
            "endpoint_stats": endpoint_stats,
            "period_days": days
        }
    
    def _hash_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
