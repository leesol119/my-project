FROM python:3.11-slim

WORKDIR /app

COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway/ .

EXPOSE 8000
CMD ["python", "main.py"]