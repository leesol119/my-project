FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치 (Railway 호환성을 위해 단순화)
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# requirements.txt 복사 및 의존성 설치
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY gateway/app/ ./app/

# 포트 노출
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 헬스 체크 제거 (Railway에서 문제가 될 수 있음)

# 애플리케이션 실행 (쉘 확장을 사용하여 환경변수 치환)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]