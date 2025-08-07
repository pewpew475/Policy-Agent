"""
Simple health check endpoint
"""

import json
from datetime import datetime

def handler(request):
    """Health check handler"""
    
    # Handle CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
    
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'services': {
                    'api': 'active',
                    'upload': 'active'
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'error': str(e)
            })
        }
