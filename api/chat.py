"""
Simple chat endpoint
"""

import json
import os
import time

def handler(request):
    """Handle chat requests"""
    
    # Handle CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
    
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    if request.get('method') != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        body = request.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        message = data.get('message', '')
        document_ids = data.get('document_ids', [])
        
        # Mock AI response
        ai_response = f"I understand you're asking: '{message}'. "
        
        if document_ids:
            ai_response += f"I've analyzed {len(document_ids)} document(s). "
        
        ai_response += "This is a demo response from the Insurance AI Assistant. The full AI integration with GLM and Gemini APIs will be available once the backend is properly configured."
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': ai_response,
                'conversation_id': 'demo-conversation',
                'response_time': 0.5,
                'sources': document_ids
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Chat failed: {str(e)}'})
        }
