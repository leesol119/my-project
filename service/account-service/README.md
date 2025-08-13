# Account Service

EriPotter 프로젝트의 로그인/회원가입 기능을 담당하는 마이크로서비스입니다.

## 주요 기능

- **로그인**: 사용자 인증 및 토큰 발급
- **회원가입**: 새로운 사용자 등록
- **사용자 관리**: 역할별 사용자 관리 (Director, Executive, Manager, Supervisor, Worker)

## 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.11
- **Deployment**: Railway

## 로컬 개발 환경

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# .env 파일 생성
RAILWAY_ENVIRONMENT=false
```

### 3. 서버 실행
```bash
# 개발 모드
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# 또는 직접 실행
python app/main.py
```

## Docker 실행

```bash
# 이미지 빌드
docker build -t account-service .

# 컨테이너 실행
docker run -p 8003:8003 account-service
```

## Railway 배포

### 1. Railway CLI 설치
```bash
npm install -g @railway/cli
```

### 2. 로그인
```bash
railway login
```

### 3. 프로젝트 초기화
```bash
railway init
```

### 4. 배포
```bash
railway up
```

### 5. 환경변수 설정
Railway 대시보드에서 다음 환경변수를 설정:
```
RAILWAY_ENVIRONMENT=true
```

## API 엔드포인트

### 기본 엔드포인트
- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스체크
- `GET /healthz` - 간단한 헬스체크

### 인증 엔드포인트
- `POST /login` - 로그인
- `POST /signup` - 회원가입

### 사용자 관리 엔드포인트
- Director 관련: `/director/*`
- Executive 관련: `/executive/*`
- Manager 관련: `/manager/*`
- Supervisor 관련: `/supervisor/*`
- Worker 관련: `/worker/*`

## 요청/응답 예시

### 로그인
```bash
POST /login
Content-Type: application/json

{
  "user_id": "test_user",
  "password": "123456"
}
```

### 회원가입
```bash
POST /signup
Content-Type: application/json

{
  "user_id": "new_user",
  "password": "123456",
  "company_id": "company_001"
}
```

## 접속 URL

| 환경 | URL | 설명 |
|------|-----|------|
| 로컬 개발 | http://localhost:8003 | 개발 환경 |
| Docker | http://localhost:8003 | Docker 환경 |
| Railway | https://your-account-service.railway.app | 프로덕션 환경 |

## 로그 확인

```bash
# Railway 로그 확인
railway logs

# Docker 로그 확인
docker logs account-service
```
