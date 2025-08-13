#!/bin/bash

# 프로덕션 CORS 테스트 스크립트
GATEWAY_URL="https://my-project-production-0a50.up.railway.app"

echo "🚀 프로덕션 CORS 테스트 시작"
echo "🔧 Gateway URL: $GATEWAY_URL"

# Gateway 헬스체크
echo "📋 Gateway 헬스체크"
curl -i "$GATEWAY_URL/healthz"

echo -e "\n"

# 프리플라이트 시뮬레이션 (프로덕션)
echo "🔄 프리플라이트 시뮬레이션 (프로덕션)"
curl -i -X OPTIONS "$GATEWAY_URL/signup" \
  -H "Origin: https://sme.eripotter.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

# 실제 로그인 요청 (프로덕션)
echo "🔐 로그인 요청 (프로덕션)"
curl -i -X POST "$GATEWAY_URL/login" \
  -H "Origin: https://sme.eripotter.com" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","password":"123"}'

echo -e "\n"

# 실제 회원가입 요청 (프로덕션)
echo "📝 회원가입 요청 (프로덕션)"
curl -i -X POST "$GATEWAY_URL/signup" \
  -H "Origin: https://sme.eripotter.com" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","password":"123","company_id":"test_company"}'

echo -e "\n"

# www 서브도메인 테스트
echo "🌐 www 서브도메인 프리플라이트 테스트"
curl -i -X OPTIONS "$GATEWAY_URL/signup" \
  -H "Origin: https://www.sme.eripotter.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"

echo -e "\n"

# Account Service 연결 테스트
echo "🔗 Account Service 연결 테스트"
curl -i "$GATEWAY_URL/test-account-service"

echo -e "\n"

echo "✅ 프로덕션 CORS 테스트 완료"
