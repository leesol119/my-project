#!/bin/bash

echo "🐳 MSA Gateway Docker Commands"
echo "================================"

echo ""
echo "📦 1. 개발 환경 실행 (Docker Compose)"
echo "   docker-compose up --build"
echo "   또는 백그라운드 실행: docker-compose up -d --build"
echo ""

echo "🏭 2. 프로덕션 환경 실행"
echo "   docker-compose -f docker-compose.prod.yml up --build"
echo ""

echo "🔨 3. 개별 Docker 이미지 빌드"
echo "   # 개발용"
echo "   docker build -f Dockerfile.dev -t msa-gateway:dev ."
echo "   # 프로덕션용"
echo "   docker build -f Dockerfile -t msa-gateway:prod ."
echo ""

echo "🚀 4. 개별 컨테이너 실행"
echo "   # 개발용"
echo "   docker run -p 8000:8000 -v \$(pwd)/app:/app/app msa-gateway:dev"
echo "   # 프로덕션용"
echo "   docker run -p 8000:8000 msa-gateway:prod"
echo ""

echo "📊 5. 컨테이너 상태 확인"
echo "   docker ps"
echo "   docker logs msa-gateway"
echo ""

echo "🛑 6. 서비스 중지"
echo "   docker-compose down"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""

echo "🧹 7. 정리"
echo "   docker-compose down -v --remove-orphans"
echo "   docker system prune -f"
echo ""

echo "🔍 8. 헬스 체크"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/api/discovery/health"
echo ""

echo "📋 9. 서비스 등록 테스트"
echo "   curl -X POST http://localhost:8000/api/discovery/services \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"service_name\":\"test-service\",\"base_url\":\"http://localhost:8080\",\"health_check_url\":\"http://localhost:8080/health\"}'"
echo ""

echo "🌐 10. 접속 URL"
echo "    Gateway: http://localhost:8000"
echo "    API Docs: http://localhost:8000/docs"
echo "    User Service: http://localhost:8001"
echo "    Product Service: http://localhost:8002"
echo "    Order Service: http://localhost:8003"
echo ""

echo "✅ 모든 준비 완료!" 