# Assessment Service

EriPotter 프로젝트의 Assessment Service입니다.

## 🚀 Railway 배포

### 1. Railway CLI 설치
```bash
npm install -g @railway/cli
```

### 2. Railway 로그인
```bash
railway login
```

### 3. 프로젝트 초기화
```bash
railway init
```

### 4. 환경 변수 설정
Railway 대시보드에서 다음 환경 변수를 설정하세요:

```
RAILWAY_ENVIRONMENT=true
API_SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 5. 배포
```bash
railway up
```

## 📋 API 엔드포인트

- `GET /` - 서비스 정보
- `GET /health` - 헬스 체크
- `GET /docs` - API 문서 (Swagger UI)
- `POST /api/v1/assessment/create` - 평가 생성
- `GET /api/v1/assessment/{assessment_id}` - 평가 정보 조회
- `GET /api/v1/assessment/{assessment_id}/result` - 평가 결과 조회

## 🔧 로컬 개발

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정
```

### 3. 서버 실행
```bash
python -m uvicorn app.main:app --reload --port 8080
```

## 🐳 Docker 실행

```bash
docker build -t assessment-service .
docker run -p 8080:8080 assessment-service
```

## 📝 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `PORT` | 서버 포트 | 8080 |
| `RAILWAY_ENVIRONMENT` | Railway 환경 여부 | false |
| `API_SECRET_KEY` | API 시크릿 키 | - |
| `JWT_SECRET_KEY` | JWT 시크릿 키 | - |
| `LOG_LEVEL` | 로그 레벨 | INFO |
| `ALLOWED_ORIGINS` | 허용된 CORS 도메인 | - |
