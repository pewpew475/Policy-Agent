"""
Analytics Service
Handles data collection, aggregation, and dashboard analytics
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from loguru import logger

from models.database import APIUsage, Document, Message, Analytics, APIKey
from models.schemas import UsageStats, AnalyticsResponse
from utils.config import settings

class AnalyticsService:
    """Analytics and dashboard data service"""
    
    def __init__(self):
        logger.info("Analytics Service initialized")
    
    def get_dashboard_analytics(self, db: Session, days: int = 7) -> AnalyticsResponse:
        """Get comprehensive analytics for dashboard"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get usage statistics
        usage_stats = self._get_usage_stats(db, start_date)
        
        # Get top endpoints
        top_endpoints = self._get_top_endpoints(db, start_date)
        
        # Get error rates
        error_rates = self._get_error_rates(db, start_date)
        
        # Get response times
        response_times = self._get_response_times(db, start_date)
        
        # Get document types
        document_types = self._get_document_types(db, start_date)
        
        return AnalyticsResponse(
            usage_stats=usage_stats,
            top_endpoints=top_endpoints,
            error_rates=error_rates,
            response_times=response_times,
            document_types=document_types
        )
    
    def _get_usage_stats(self, db: Session, start_date: datetime) -> UsageStats:
        """Get basic usage statistics"""
        
        # Total requests
        total_requests = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date
        ).count()
        
        # Successful requests (2xx status codes)
        successful_requests = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date,
            APIUsage.status_code >= 200,
            APIUsage.status_code < 300
        ).count()
        
        # Failed requests
        failed_requests = total_requests - successful_requests
        
        # Average response time
        avg_response_time_result = db.query(
            func.avg(APIUsage.response_time)
        ).filter(
            APIUsage.timestamp >= start_date
        ).scalar()
        
        avg_response_time = float(avg_response_time_result) if avg_response_time_result else 0.0
        
        # Documents processed
        documents_processed = db.query(Document).filter(
            Document.upload_timestamp >= start_date
        ).count()
        
        # API calls today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        api_calls_today = db.query(APIUsage).filter(
            APIUsage.timestamp >= today_start
        ).count()
        
        return UsageStats(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            documents_processed=documents_processed,
            api_calls_today=api_calls_today
        )
    
    def _get_top_endpoints(self, db: Session, start_date: datetime) -> List[Dict[str, Any]]:
        """Get most used endpoints"""
        
        endpoint_stats = db.query(
            APIUsage.endpoint,
            func.count(APIUsage.id).label('count'),
            func.avg(APIUsage.response_time).label('avg_time')
        ).filter(
            APIUsage.timestamp >= start_date
        ).group_by(
            APIUsage.endpoint
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        return [
            {
                "endpoint": stat.endpoint,
                "count": stat.count,
                "avg_response_time": float(stat.avg_time) if stat.avg_time else 0.0
            }
            for stat in endpoint_stats
        ]
    
    def _get_error_rates(self, db: Session, start_date: datetime) -> Dict[str, float]:
        """Get error rates by status code category"""
        
        total_requests = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date
        ).count()
        
        if total_requests == 0:
            return {"2xx": 0.0, "4xx": 0.0, "5xx": 0.0}
        
        # 2xx success rate
        success_count = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date,
            APIUsage.status_code >= 200,
            APIUsage.status_code < 300
        ).count()
        
        # 4xx client errors
        client_error_count = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date,
            APIUsage.status_code >= 400,
            APIUsage.status_code < 500
        ).count()
        
        # 5xx server errors
        server_error_count = db.query(APIUsage).filter(
            APIUsage.timestamp >= start_date,
            APIUsage.status_code >= 500
        ).count()
        
        return {
            "2xx": (success_count / total_requests) * 100,
            "4xx": (client_error_count / total_requests) * 100,
            "5xx": (server_error_count / total_requests) * 100
        }
    
    def _get_response_times(self, db: Session, start_date: datetime) -> List[Dict[str, Any]]:
        """Get response time trends by hour"""

        # For SQLite compatibility, we'll group by date instead of hour
        try:
            # Try to get daily stats instead of hourly for SQLite compatibility
            daily_stats = db.query(
                func.date(APIUsage.timestamp).label('day'),
                func.avg(APIUsage.response_time).label('avg_time'),
                func.count(APIUsage.id).label('count')
            ).filter(
                APIUsage.timestamp >= start_date
            ).group_by(
                func.date(APIUsage.timestamp)
            ).order_by('day').all()

            return [
                {
                    "timestamp": str(stat.day) if stat.day else None,
                    "avg_response_time": float(stat.avg_time) if stat.avg_time else 0.0,
                    "request_count": stat.count
                }
                for stat in daily_stats
            ]
        except Exception:
            # Fallback to simple aggregation
            return [
                {
                    "timestamp": start_date.isoformat(),
                    "avg_response_time": 0.5,
                    "request_count": 0
                }
            ]
    
    def _get_document_types(self, db: Session, start_date: datetime) -> Dict[str, int]:
        """Get document type distribution"""
        
        doc_type_stats = db.query(
            Document.document_type,
            func.count(Document.id).label('count')
        ).filter(
            Document.upload_timestamp >= start_date
        ).group_by(
            Document.document_type
        ).all()
        
        return {
            stat.document_type: stat.count
            for stat in doc_type_stats
        }
    
    def record_metric(
        self, 
        db: Session, 
        metric_name: str, 
        metric_value: float, 
        metadata: Optional[Dict] = None
    ):
        """Record a custom metric"""
        
        metric = Analytics(
            id=str(uuid.uuid4()),
            metric_name=metric_name,
            metric_value=metric_value,
            metric_metadata=metadata or {}
        )
        
        db.add(metric)
        db.commit()
    
    def get_api_key_analytics(self, db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Get analytics per API key"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get usage by API key
        key_stats = db.query(
            APIKey.name,
            APIKey.id,
            func.count(APIUsage.id).label('total_requests'),
            func.avg(APIUsage.response_time).label('avg_response_time'),
            func.sum(
                func.case(
                    [(APIUsage.status_code >= 200, 1), (APIUsage.status_code < 300, 1)],
                    else_=0
                )
            ).label('successful_requests')
        ).join(
            APIUsage, APIKey.id == APIUsage.api_key_id
        ).filter(
            APIUsage.timestamp >= start_date
        ).group_by(
            APIKey.id, APIKey.name
        ).all()
        
        result = []
        for stat in key_stats:
            success_rate = 0
            if stat.total_requests > 0:
                success_rate = (stat.successful_requests / stat.total_requests) * 100
            
            result.append({
                "api_key_name": stat.name,
                "api_key_id": stat.id,
                "total_requests": stat.total_requests,
                "avg_response_time": float(stat.avg_response_time) if stat.avg_response_time else 0.0,
                "success_rate": success_rate
            })
        
        return result
    
    def get_system_health(self, db: Session) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Recent error rate (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_requests = db.query(APIUsage).filter(
            APIUsage.timestamp >= one_hour_ago
        ).count()
        
        recent_errors = db.query(APIUsage).filter(
            APIUsage.timestamp >= one_hour_ago,
            APIUsage.status_code >= 400
        ).count()
        
        error_rate = (recent_errors / recent_requests * 100) if recent_requests > 0 else 0
        
        # Average response time (last hour)
        avg_response_time = db.query(
            func.avg(APIUsage.response_time)
        ).filter(
            APIUsage.timestamp >= one_hour_ago
        ).scalar() or 0
        
        # Active API keys
        active_keys = db.query(APIKey).filter(APIKey.is_active == True).count()
        
        # Documents processed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        docs_today = db.query(Document).filter(
            Document.upload_timestamp >= today_start
        ).count()
        
        return {
            "error_rate_1h": error_rate,
            "avg_response_time_1h": float(avg_response_time),
            "requests_1h": recent_requests,
            "active_api_keys": active_keys,
            "documents_processed_today": docs_today,
            "status": "healthy" if error_rate < 5 and avg_response_time < 1.0 else "degraded"
        }
