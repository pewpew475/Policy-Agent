"""
Simple test endpoint for Vercel deployment verification
"""

def handler(request):
    """Simple test handler"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': {
            'message': 'API is working!',
            'timestamp': '2024-01-01T00:00:00Z',
            'status': 'healthy'
        }
    }
