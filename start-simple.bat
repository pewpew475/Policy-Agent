@echo off
echo ========================================
echo Insurance AI Assistant - Quick Start
echo ========================================
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd python-backend && python main.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Services Starting...
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause > nul

start http://localhost:3000

echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause
