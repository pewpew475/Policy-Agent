#!/usr/bin/env python3
"""
Single-command startup script for Insurance AI Assistant
Starts both frontend and backend services
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class InsuranceAIStarter:
    """Manages startup of both frontend and backend services"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "python-backend"
        self.frontend_dir = self.project_root
        
        self.backend_process = None
        self.frontend_process = None
        self.running = True
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import fastapi
            import uvicorn
            import groq
            print("✅ Python backend dependencies found")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("Installing Python dependencies...")
            self.install_python_deps()
        
        # Check Node.js dependencies
        if not (self.frontend_dir / "node_modules").exists():
            print("❌ Node.js dependencies not found")
            print("Installing Node.js dependencies...")
            self.install_node_deps()
        else:
            print("✅ Node.js dependencies found")
    
    def install_python_deps(self):
        """Install Python dependencies"""
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.backend_dir / "requirements.txt")
            ], check=True, cwd=self.backend_dir)
            print("✅ Python dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            sys.exit(1)
    
    def install_node_deps(self):
        """Install Node.js dependencies"""
        try:
            # Try different npm commands for Windows compatibility
            npm_commands = ["npm", "npm.cmd", "npm.exe"]

            for npm_cmd in npm_commands:
                try:
                    subprocess.run([npm_cmd, "install"], check=True, cwd=self.frontend_dir, shell=True)
                    print("✅ Node.js dependencies installed")
                    return
                except FileNotFoundError:
                    continue
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install Node.js dependencies with {npm_cmd}: {e}")
                    continue

            print("❌ Could not install Node.js dependencies with any npm command")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            sys.exit(1)
    
    def setup_environment(self):
        """Setup environment variables and configuration"""
        print("⚙️ Setting up environment...")
        
        # Check if .env exists in backend
        env_file = self.backend_dir / ".env"
        if not env_file.exists():
            print("❌ Backend .env file not found")
            print("Please create python-backend/.env with required configuration")
            sys.exit(1)
        
        # Create uploads directory
        uploads_dir = self.backend_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        # Create processed documents directory
        processed_dir = self.backend_dir / "processed_documents"
        processed_dir.mkdir(exist_ok=True)
        
        # Create logs directory
        logs_dir = self.backend_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        print("✅ Environment setup complete")
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting backend server...")
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ], cwd=self.backend_dir)
            
            # Wait a moment for backend to start
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started on http://localhost:8000")
                return True
            else:
                print("❌ Backend server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Next.js frontend"""
        print("🚀 Starting frontend server...")

        try:
            # Try different ways to run npm on Windows
            npm_commands = ["npm", "npm.cmd", "npm.exe"]

            for npm_cmd in npm_commands:
                try:
                    self.frontend_process = subprocess.Popen([
                        npm_cmd, "run", "dev"
                    ], cwd=self.frontend_dir, shell=True)

                    # Wait a moment for frontend to start
                    time.sleep(5)

                    if self.frontend_process.poll() is None:
                        print("✅ Frontend server started on http://localhost:3000")
                        return True
                    else:
                        print(f"❌ Frontend server failed to start with {npm_cmd}")
                        continue

                except FileNotFoundError:
                    print(f"❌ {npm_cmd} not found, trying next...")
                    continue
                except Exception as e:
                    print(f"❌ Failed to start frontend with {npm_cmd}: {e}")
                    continue

            print("❌ Could not start frontend with any npm command")
            return False

        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            time.sleep(5)
            
            # Check backend
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️ Backend process died, restarting...")
                self.start_backend()
            
            # Check frontend
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️ Frontend process died, restarting...")
                self.start_frontend()
    
    def stop_services(self):
        """Stop all services"""
        print("\n🛑 Stopping services...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=10)
                print("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("🔪 Backend force killed")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
                print("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("🔪 Frontend force killed")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        print("🏥 Insurance AI Assistant - Starting Up")
        print("=" * 50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Check dependencies
            self.check_dependencies()
            
            # Setup environment
            self.setup_environment()
            
            # Start backend
            if not self.start_backend():
                print("❌ Failed to start backend, exiting")
                sys.exit(1)
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Failed to start frontend, exiting")
                self.stop_services()
                sys.exit(1)
            
            print("\n🎉 Insurance AI Assistant is running!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend API: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            print("\nPress Ctrl+C to stop all services")
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_services()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.stop_services()
            sys.exit(1)

if __name__ == "__main__":
    starter = InsuranceAIStarter()
    starter.run()
