"""
Multi-AI Service for processing large documents
Distributes document chunks across GLM-4.5-FLASH and Gemini-2.0-FLASH APIs
"""

import asyncio
import json
import math
from typing import List, Dict, Optional, AsyncGenerator, Tuple
import httpx
from loguru import logger
from utils.config import settings


class MultiAIService:
    """Service for processing large documents using multiple AI APIs"""
    
    def __init__(self):
        self.glm_api_key = settings.GLM_API_KEY
        self.glm_api_url = settings.GLM_API_URL
        self.gemini_api_keys = settings.GEMINI_API_KEYS
        self.gemini_api_url = settings.GEMINI_API_URL
        
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Available AI APIs (GLM + Gemini keys)
        self.available_apis = []
        if self.glm_api_key:
            self.available_apis.append(("glm", self.glm_api_key))
        
        for i, key in enumerate(self.gemini_api_keys):
            if key:
                self.available_apis.append((f"gemini_{i+1}", key))
        
        logger.info(f"Multi-AI Service initialized with {len(self.available_apis)} AI APIs")
    
    def split_document(self, text: str, num_chunks: int) -> List[str]:
        """Split document text into equal chunks"""
        if not text or num_chunks <= 1:
            return [text]
        
        # Calculate chunk size
        chunk_size = math.ceil(len(text) / num_chunks)
        chunks = []
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    async def query_glm(self, api_key: str, prompt: str, document_chunk: str) -> str:
        """Query GLM-4.5-FLASH API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an insurance document analysis expert. Analyze the provided document chunk and answer the user's question based only on the information in this chunk. If the answer is not in this chunk, respond with 'NOT_FOUND_IN_CHUNK'."
                },
                {
                    "role": "user",
                    "content": f"Document chunk:\n{document_chunk}\n\nQuestion: {prompt}"
                }
            ]
            
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
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"GLM API Error: {response.status_code}")
                return "ERROR: GLM API failed"
                
        except Exception as e:
            logger.error(f"GLM query error: {str(e)}")
            return f"ERROR: {str(e)}"
    
    async def query_gemini(self, api_key: str, prompt: str, document_chunk: str) -> str:
        """Query Gemini-2.0-FLASH API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"You are an insurance document analysis expert. Analyze the provided document chunk and answer the user's question based only on the information in this chunk. If the answer is not in this chunk, respond with 'NOT_FOUND_IN_CHUNK'.\n\nDocument chunk:\n{document_chunk}\n\nQuestion: {prompt}"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1024
                }
            }
            
            url = f"{self.gemini_api_url}?key={api_key}"
            response = await self.http_client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    return "ERROR: No response from Gemini"
            else:
                logger.error(f"Gemini API Error: {response.status_code}")
                return "ERROR: Gemini API failed"
                
        except Exception as e:
            logger.error(f"Gemini query error: {str(e)}")
            return f"ERROR: {str(e)}"
    
    async def process_large_document(self, document_text: str, user_question: str) -> AsyncGenerator[str, None]:
        """Process large document using multiple AI APIs"""
        
        if not self.available_apis:
            yield "❌ No AI APIs available. Please configure GLM or Gemini API keys."
            return
        
        # Determine number of chunks based on document size and available APIs
        document_length = len(document_text)
        max_chunk_size = 8000  # Conservative chunk size for AI processing
        
        if document_length <= max_chunk_size:
            # Small document, use single API (silently)
            api_type, api_key = self.available_apis[0]

            if api_type == "glm":
                result = await self.query_glm(api_key, user_question, document_text)
            else:
                result = await self.query_gemini(api_key, user_question, document_text)

            yield result
            return
        
        # Large document, split across multiple APIs
        num_chunks = min(len(self.available_apis), math.ceil(document_length / max_chunk_size))
        chunks = self.split_document(document_text, num_chunks)

        # Process chunks in parallel (silently)
        tasks = []
        for i, chunk in enumerate(chunks):
            api_type, api_key = self.available_apis[i % len(self.available_apis)]

            if api_type == "glm":
                task = self.query_glm(api_key, user_question, chunk)
            else:
                task = self.query_gemini(api_key, user_question, chunk)

            tasks.append((i, api_type, task))

        # Wait for all tasks to complete (silently)
        results = []

        for i, api_type, task in tasks:
            try:
                result = await task
                results.append((i, api_type, result))
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                results.append((i, api_type, f"ERROR: {str(e)}"))

        # Combine and analyze results - only return the final answer
        valid_results = []
        for i, api_type, result in results:
            if result and not result.startswith("ERROR") and "NOT_FOUND_IN_CHUNK" not in result:
                valid_results.append(result.strip())

        if valid_results:
            # Combine all valid results into a single comprehensive answer
            if len(valid_results) == 1:
                # Single result, return as-is
                yield valid_results[0]
            else:
                # Multiple results, combine intelligently
                combined_answer = self._combine_multiple_answers(valid_results, user_question)
                yield combined_answer
        else:
            yield "I couldn't find the answer to your question in the uploaded document. Please check if the information is present or try rephrasing your question."

    def _combine_multiple_answers(self, results: List[str], user_question: str) -> str:
        """Intelligently combine multiple AI responses into a single coherent answer"""

        # Remove duplicates and very similar responses
        unique_results = []
        for result in results:
            is_duplicate = False
            for existing in unique_results:
                # Simple similarity check - if 80% of words are the same, consider duplicate
                result_words = set(result.lower().split())
                existing_words = set(existing.lower().split())
                if len(result_words & existing_words) / max(len(result_words), len(existing_words)) > 0.8:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_results.append(result)

        if len(unique_results) == 1:
            return unique_results[0]

        # If multiple unique answers, combine them logically
        combined = ""

        # Check if answers are complementary (different aspects of same question)
        if any(keyword in user_question.lower() for keyword in ['what', 'how much', 'when', 'where', 'who']):
            # For factual questions, combine all relevant information
            for i, result in enumerate(unique_results):
                if i == 0:
                    combined = result
                else:
                    # Add additional information if it's not already covered
                    if not any(word in combined.lower() for word in result.lower().split()[:5]):
                        combined += f"\n\nAdditionally: {result}"
        else:
            # For other questions, provide the most comprehensive answer
            longest_answer = max(unique_results, key=len)
            combined = longest_answer

            # Add any unique information from other answers
            for result in unique_results:
                if result != longest_answer:
                    # Extract unique information (simple approach)
                    result_sentences = result.split('.')
                    for sentence in result_sentences:
                        if sentence.strip() and not any(sentence.strip().lower() in combined.lower() for _ in [1]):
                            if len(sentence.strip()) > 20:  # Only add substantial sentences
                                combined += f" {sentence.strip()}."

        return combined.strip()

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
