FROM python:3.11-slim

WORKDIR /app

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .
RUN mv gateway/main.py ./main.py && mv gateway/app ./app

# 포트 노출
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 애플리케이션 실행 (쉘 확장으로 $PORT 치환)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]