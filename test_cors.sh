#!/bin/bash

# CORS 테스트 스크립트
echo "🚀 CORS 테스트 시작"

# Gateway 헬스체크
echo "📋 Gateway 헬스체크"
curl -i http://localhost:8080/healthz

echo -e "\n"

# Account Service 헬스체크
echo "📋 Account Service 헬스체크"
curl -i http://localhost:8003/health

echo -e "\n"

# 프리플라이트 시뮬레이션 (로컬)
echo "🔄 프리플라이트 시뮬레이션 (로컬)"
curl -i -X OPTIONS "http://localhost:8080/signup" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

# 다양한 로컬 포트 테스트
echo "🔄 다양한 로컬 포트 테스트"
curl -i -X OPTIONS "http://localhost:8080/signup" \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

curl -i -X OPTIONS "http://localhost:8080/signup" \
  -H "Origin: http://127.0.0.1:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

curl -i -X OPTIONS "http://localhost:8080/signup" \
  -H "Origin: http://192.168.0.99:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

# 실제 로그인 요청 (로컬)
echo "🔐 로그인 요청 (로컬)"
curl -i -X POST "http://localhost:8080/login" \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","password":"123"}'

echo -e "\n"

# 실제 회원가입 요청 (로컬)
echo "📝 회원가입 요청 (로컬)"
curl -i -X POST "http://localhost:8080/signup" \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","password":"123","company_id":"test_company"}'

echo -e "\n"

# Account Service 직접 테스트
echo "🔐 Account Service 직접 로그인"
curl -i -X POST "http://localhost:8003/login" \
  -H "Origin: http://localhost:8080" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","password":"123"}'

echo -e "\n"

echo "✅ CORS 테스트 완료"
