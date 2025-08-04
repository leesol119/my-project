FROM python:3.11-slim

WORKDIR /app

# gateway 안의 requirements.txt를 정확히 복사
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# gateway 폴더 안의 소스코드만 복사
COPY gateway/ .

EXPOSE 8000

CMD ["python", "main.py"]
