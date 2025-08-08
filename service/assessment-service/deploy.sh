#!/bin/bash

echo "🚀 Assessment Service Railway 배포 시작..."

# Railway CLI 설치 확인
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI가 설치되지 않았습니다."
    echo "npm install -g @railway/cli"
    exit 1
fi

# Railway 로그인 확인
if ! railway whoami &> /dev/null; then
    echo "❌ Railway에 로그인되지 않았습니다."
    echo "railway login"
    exit 1
fi

# 프로젝트 초기화
if [ ! -f ".railway" ]; then
    echo "📦 Railway 프로젝트 초기화..."
    railway init
fi

# 배포 실행
echo "🚀 배포 시작..."
railway up

echo "✅ 배포 완료!"
railway status
