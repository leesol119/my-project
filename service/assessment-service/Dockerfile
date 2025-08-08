FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 보안을 위한 비root 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 작업 디렉토리 설정
WORKDIR /app

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 파일 권한 설정
RUN chown -R appuser:appuser /app

# 비root 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8080

# 헬스체크 추가 (더 안정적인 버전)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health/minimal || curl -f http://localhost:8080/health/simple || exit 1

# Railway 환경에서 실행
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
