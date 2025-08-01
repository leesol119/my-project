#!/bin/bash

echo "🚀 Starting EriPotter Production Environment..."

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start all services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Show status
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 Services are running at:"
echo "   Frontend: http://localhost:3000"
echo "   Gateway:  http://localhost:8000"
echo "   Gateway API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs: docker-compose -f docker-compose.prod.yml logs -f [service-name]"
echo "🛑 To stop: docker-compose -f docker-compose.prod.yml down" 