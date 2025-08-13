#!/bin/bash

# Railway 환경변수 처리
PORT=${PORT:-8006}
echo "🚀 Starting Account Service on port: $PORT"

# Python 애플리케이션 시작
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
