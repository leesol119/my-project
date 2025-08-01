@echo off
echo 🚀 Starting EriPotter Development Environment...

REM Stop any existing containers
echo 📦 Stopping existing containers...
docker-compose down

REM Build and start all services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Show status
echo 📊 Service Status:
docker-compose ps

echo.
echo 🌐 Services are running at:
echo    Frontend: http://localhost:3000
echo    Gateway:  http://localhost:8080
echo    Gateway API Docs: http://localhost:8080/docs

echo.
echo 📝 To view logs: docker-compose logs -f [service-name]
echo 🛑 To stop: docker-compose down
pause 