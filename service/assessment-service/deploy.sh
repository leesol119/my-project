#!/bin/bash

# Assessment Service Railway 배포 스크립트

echo "🚀 Assessment Service Railway 배포 시작..."

# Railway CLI 설치 확인
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI가 설치되지 않았습니다."
    echo "다음 명령어로 설치하세요: npm install -g @railway/cli"
    exit 1
fi

# Railway 로그인 확인
if ! railway whoami &> /dev/null; then
    echo "❌ Railway에 로그인되지 않았습니다."
    echo "다음 명령어로 로그인하세요: railway login"
    exit 1
fi

# 현재 디렉토리 확인
echo "📁 현재 디렉토리: $(pwd)"
echo "📁 파일 목록:"
ls -la

# Dockerfile 존재 확인
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile 발견"
else
    echo "❌ Dockerfile이 없습니다. NIXPACKS 빌더를 사용합니다."
fi

# 프로젝트 초기화 (이미 초기화된 경우 스킵)
if [ ! -f ".railway" ]; then
    echo "📦 Railway 프로젝트 초기화..."
    railway init
fi

# 환경 변수 설정 확인
echo "🔧 환경 변수 설정 확인..."
if [ -z "$RAILWAY_ENVIRONMENT" ]; then
    echo "⚠️  RAILWAY_ENVIRONMENT 환경 변수가 설정되지 않았습니다."
    echo "Railway 대시보드에서 환경 변수를 설정하세요."
fi

# 배포 실행
echo "🚀 배포 시작..."
railway up

echo "✅ 배포 완료!"
echo "📋 배포된 서비스 URL을 확인하려면: railway status"
