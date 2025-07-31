# 경량 Python 이미지
FROM python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# 필수 시스템 패키지 (필요시만 설치)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# pip 최신화
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# gateway/requirements.txt 복사 후 설치
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# gateway 소스 복사
COPY gateway/ ./app/

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Railway에서 PORT 환경변수를 주입 → 없으면 기본값 8000
ENV PORT=8000

# 포트 노출
EXPOSE $PORT

# FastAPI 실행 (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
