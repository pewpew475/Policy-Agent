"""
Simple file upload endpoint using Vercel Blob
"""

import json
import os
import time
from urllib.parse import parse_qs

def handler(request):
    """Handle file upload requests"""
    
    # Handle CORS preflight
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': ''
        }
    
    # Only allow POST requests
    if request.get('method') != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # For now, return a mock response since we need to set up Vercel Blob properly
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'uploaded_documents': [
                    {
                        'document_id': 'mock-doc-1',
                        'filename': 'uploaded-document.pdf',
                        'status': 'ready',
                        'file_size': 1024,
                        'document_type': 'pdf'
                    }
                ]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': f'Upload failed: {str(e)}'})
        }
