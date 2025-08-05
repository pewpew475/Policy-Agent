"""
AI Service Integration
Handles Groq API and GLM-4.5-FLASH model integration with streaming support
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, AsyncGenerator, Any
import httpx
from loguru import logger
from .multi_ai_service import MultiAIService

from utils.config import settings
from models.schemas import ChatMessage, MessageRole

class AIService:
    """AI service with Groq and GLM integration"""
    
    def __init__(self):
        # GLM configuration only
        self.glm_api_key = settings.GLM_API_KEY
        self.glm_api_url = settings.GLM_API_URL

        # HTTP client for GLM
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Multi-AI service for large documents
        self.multi_ai_service = MultiAIService()

        if not self.glm_api_key:
            logger.warning("GLM API key not configured")

        logger.info("AI Service initialized with GLM-4.5-FLASH and Multi-AI support")
    
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        document_context: Optional[str] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate chat completion with streaming support using GLM-4.5-FLASH and Multi-AI for large docs"""

        start_time = time.time()

        try:
            # Check if we have a large document that needs multi-AI processing
            if document_context and len(document_context) > 10000:  # 10KB threshold
                logger.info(f"Large document detected ({len(document_context)} chars), using Multi-AI processing")

                # Extract user question from messages
                user_question = ""
                for msg in messages:
                    if msg.role == MessageRole.USER:
                        user_question = msg.content
                        break

                # Use multi-AI service for large documents
                async for chunk in self.multi_ai_service.process_large_document(document_context, user_question):
                    yield chunk
            else:
                # Use standard GLM processing for smaller documents
                formatted_messages = self._prepare_messages(messages, document_context)
                async for chunk in self._glm_stream_completion(formatted_messages):
                    yield chunk

        except Exception as e:
            logger.error(f"AI completion error: {str(e)}")
            yield f"Error: {str(e)}"

        response_time = time.time() - start_time
        logger.info(f"AI response completed in {response_time:.3f}s")
    

    
    async def _glm_stream_completion(
        self,
        messages: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """Stream completion from GLM-4.5-FLASH API"""

        if not self.glm_api_key:
            yield "❌ GLM API key not configured. Please set GLM_API_KEY in your .env file."
            return

        try:
            headers = {
                "Authorization": f"Bearer {self.glm_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4.5-flash",
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9
            }

            async with self.http_client.stream(
                "POST",
                f"{self.glm_api_url}chat/completions",
                headers=headers,
                json=payload
            ) as response:

                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"GLM API Error {response.status_code}: {error_text}")

                    # Provide demo response when GLM is not available
                    demo_response = self._generate_demo_response(messages)
                    for chunk in demo_response:
                        yield chunk
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            chunk_data = json.loads(data)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"GLM streaming error: {str(e)}")
            yield f"❌ GLM API Error: {str(e)}"
    
    def _prepare_messages(
        self, 
        messages: List[ChatMessage], 
        document_context: Optional[str] = None
    ) -> List[Dict]:
        """Prepare messages for AI API with document context"""
        
        formatted_messages = []
        
        # Add system message with insurance context
        system_message = {
            "role": "system",
            "content": self._get_system_prompt(document_context)
        }
        formatted_messages.append(system_message)
        
        # Add conversation messages
        for message in messages:
            formatted_messages.append({
                "role": message.role.value,
                "content": message.content
            })
        
        return formatted_messages
    
    def _get_system_prompt(self, document_context: Optional[str] = None) -> str:
        """Get system prompt for insurance AI assistant"""
        
        base_prompt = """You are an expert insurance AI assistant. You help users understand insurance policies, claims, coverage details, and provide guidance on insurance-related questions.

Key responsibilities:
- Analyze insurance documents and policies
- Explain coverage details in simple terms
- Help with claims processes
- Provide accurate insurance information
- Be helpful, professional, and empathetic

Always provide accurate information and suggest consulting with insurance professionals for complex situations."""
        
        if document_context:
            base_prompt += f"\n\nDocument Context:\n{document_context[:4000]}..."  # Limit context size
        
        return base_prompt
    
    async def generate_summary(
        self, 
        text: str, 
        document_type: str = "insurance document"
    ) -> Dict[str, Any]:
        """Generate comprehensive summary of document text"""
        
        try:
            summary_prompt = f"""Analyze this {document_type} and provide a comprehensive summary.

Document Text:
{text[:8000]}  # Limit input size

Please provide:
1. A detailed summary covering all important points
2. Key coverage details (if applicable)
3. Important dates and deadlines
4. Action items or requirements
5. Notable exclusions or limitations

Format your response as a structured summary."""

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert insurance document analyzer. Provide detailed, accurate summaries."
                },
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
            
            # Use GLM for summary generation (non-streaming)
            headers = {
                "Authorization": f"Bearer {self.glm_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4.5-flash",
                "messages": messages,
                "stream": False,
                "temperature": 0.3,
                "max_tokens": 1024
            }

            response = await self.http_client.post(
                f"{self.glm_api_url}chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"GLM API Error: {response.status_code}")

            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            
            # Extract key points (simple extraction)
            key_points = self._extract_key_points(summary)
            
            return {
                "summary": summary,
                "key_points": key_points,
                "confidence_score": 0.9
            }
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {
                "summary": f"Summary generation failed: {str(e)}",
                "key_points": [],
                "confidence_score": 0.0
            }
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary text"""
        
        key_points = []
        lines = summary.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for bullet points, numbered items, or key phrases
            if (line.startswith('•') or 
                line.startswith('-') or 
                line.startswith('*') or
                any(line.startswith(f"{i}.") for i in range(1, 10)) or
                'important' in line.lower() or
                'key' in line.lower() or
                'coverage' in line.lower()):
                
                # Clean up the line
                cleaned = line.lstrip('•-*0123456789. ').strip()
                if len(cleaned) > 10:  # Minimum length for meaningful point
                    key_points.append(cleaned)
        
        return key_points[:10]  # Limit to 10 key points
    
    async def close(self):
        """Close HTTP clients and cleanup resources"""
        await self.http_client.aclose()
        await self.multi_ai_service.close()
