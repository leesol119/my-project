@echo off
echo 🚀 Starting EriPotter Production Environment...

REM Stop any existing containers
echo 📦 Stopping existing containers...
docker-compose -f docker-compose.prod.yml down

REM Build and start all services
echo 🔨 Building and starting services...
docker-compose -f docker-compose.prod.yml up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak > nul

REM Show status
echo 📊 Service Status:
docker-compose -f docker-compose.prod.yml ps

echo.
echo 🌐 Services are running at:
echo    Frontend: http://localhost:3000
echo    Gateway:  http://localhost:8000
echo    Gateway API Docs: http://localhost:8000/docs
echo.
echo 📝 To view logs: docker-compose -f docker-compose.prod.yml logs -f [service-name]
echo 🛑 To stop: docker-compose -f docker-compose.prod.yml down
pause 