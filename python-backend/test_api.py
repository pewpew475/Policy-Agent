#!/usr/bin/env python3
"""
Comprehensive test suite for Insurance AI Backend
Tests all endpoints and validates functionality
"""

import asyncio
import json
import time
from pathlib import Path
import httpx
from loguru import logger

class InsuranceAITester:
    """Test suite for Insurance AI Backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
    async def test_health_check(self):
        """Test health check endpoint"""
        logger.info("🔍 Testing health check...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_success("Health check", "Service is healthy")
                    return True
                else:
                    self.log_error("Health check", f"Unhealthy status: {data}")
                    return False
            else:
                self.log_error("Health check", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("Health check", str(e))
            return False
    
    async def test_api_key_generation(self):
        """Test API key generation"""
        logger.info("🔑 Testing API key generation...")
        
        try:
            payload = {
                "name": "Test API Key",
                "description": "Generated during testing",
                "rate_limit": 100
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/keys/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("api_key") and data["api_key"].startswith("iai_"):
                    self.log_success("API key generation", f"Generated key: {data['name']}")
                    return data["api_key"]
                else:
                    self.log_error("API key generation", "Invalid API key format")
                    return None
            else:
                self.log_error("API key generation", f"Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error("API key generation", str(e))
            return None
    
    async def test_document_upload(self):
        """Test document upload with a sample text file"""
        logger.info("📄 Testing document upload...")
        
        try:
            # Create a sample text file
            sample_content = """
            INSURANCE POLICY DOCUMENT
            
            Policy Number: INS-2024-001
            Policyholder: John Doe
            Coverage Type: Auto Insurance
            Premium: $1,200 annually
            
            Coverage Details:
            - Liability: $100,000
            - Collision: $50,000
            - Comprehensive: $25,000
            
            Effective Date: January 1, 2024
            Expiration Date: December 31, 2024
            
            Important Notes:
            - Deductible: $500
            - Coverage applies to vehicle VIN: 1234567890
            """
            
            files = {
                "file": ("test_policy.txt", sample_content.encode(), "text/plain")
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/documents/upload",
                files=files
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("document_id") and data.get("extracted_text"):
                    self.log_success("Document upload", f"Uploaded: {data['filename']}")
                    return data["document_id"]
                else:
                    self.log_error("Document upload", "Missing document data")
                    return None
            else:
                self.log_error("Document upload", f"Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error("Document upload", str(e))
            return None
    
    async def test_chat_completion(self, document_id: str = None):
        """Test chat completion endpoint"""
        logger.info("💬 Testing chat completion...")
        
        try:
            payload = {
                "message": "What is the coverage amount for liability in this policy?",
                "stream": False
            }
            
            if document_id:
                payload["document_ids"] = [document_id]
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message"):
                    self.log_success("Chat completion", f"Response length: {len(data['message'])}")
                    return True
                else:
                    self.log_error("Chat completion", "Empty response")
                    return False
            else:
                self.log_error("Chat completion", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("Chat completion", str(e))
            return False
    
    async def test_frontend_integration(self):
        """Test frontend integration endpoint"""
        logger.info("🌐 Testing frontend integration...")
        
        try:
            # Test the endpoint that the frontend will use
            data = {
                "message": "Hello, I need help with my insurance policy"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/frontend/message",
                data=data
            )
            
            if response.status_code == 200:
                # This should return a streaming response
                self.log_success("Frontend integration", "Endpoint accessible")
                return True
            else:
                self.log_error("Frontend integration", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("Frontend integration", str(e))
            return False
    
    async def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        logger.info("📊 Testing analytics dashboard...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/analytics/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if "usage_stats" in data:
                    self.log_success("Analytics dashboard", "Data retrieved successfully")
                    return True
                else:
                    self.log_error("Analytics dashboard", "Missing usage stats")
                    return False
            else:
                self.log_error("Analytics dashboard", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("Analytics dashboard", str(e))
            return False
    
    async def test_system_health(self):
        """Test system health endpoint"""
        logger.info("🏥 Testing system health...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/analytics/health")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data:
                    self.log_success("System health", f"Status: {data['status']}")
                    return True
                else:
                    self.log_error("System health", "Missing status")
                    return False
            else:
                self.log_error("System health", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error("System health", str(e))
            return False
    
    def log_success(self, test_name: str, message: str):
        """Log successful test"""
        result = {"test": test_name, "status": "PASS", "message": message}
        self.test_results.append(result)
        logger.success(f"✅ {test_name}: {message}")
    
    def log_error(self, test_name: str, message: str):
        """Log failed test"""
        result = {"test": test_name, "status": "FAIL", "message": message}
        self.test_results.append(result)
        logger.error(f"❌ {test_name}: {message}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Insurance AI Backend Tests")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # Test basic connectivity
        if not await self.test_health_check():
            logger.error("❌ Health check failed - backend may not be running")
            return False
        
        # Test API key generation
        api_key = await self.test_api_key_generation()
        
        # Test document upload
        document_id = await self.test_document_upload()
        
        # Test chat completion
        await self.test_chat_completion(document_id)
        
        # Test frontend integration
        await self.test_frontend_integration()
        
        # Test analytics
        await self.test_analytics_dashboard()
        await self.test_system_health()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        duration = time.time() - start_time
        
        logger.info("=" * 50)
        logger.info(f"📊 Test Results Summary")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Duration: {duration:.2f}s")
        
        if failed_tests == 0:
            logger.success("🎉 All tests passed!")
            return True
        else:
            logger.error(f"❌ {failed_tests} tests failed")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = InsuranceAITester()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    finally:
        await tester.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
