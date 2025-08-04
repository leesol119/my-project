FROM python:3.11-slim

WORKDIR /app

# 루트 기준으로 gateway/requirements.txt 복사
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 루트 기준으로 gateway 폴더 전체 복사
COPY gateway/ .

EXPOSE 8000

# gateway 안에 있는 main.py 실행
CMD ["python", "main.py"]
