# MSA Gateway Service

FastAPI 기반의 마이크로서비스 아키텍처 게이트웨이입니다. 프록시 패턴을 사용하여 서비스 디스커버리와 라우팅을 제공합니다.

## 주요 기능

- **서비스 디스커버리**: 동적 서비스 등록/해제 및 상태 모니터링
- **프록시 패턴**: 모든 HTTP 메서드를 지원하는 프록시 라우팅
- **헬스 체크**: 자동 서비스 상태 모니터링
- **로드 밸런싱**: 건강한 서비스로만 요청 라우팅
- **CORS 지원**: 크로스 오리진 요청 처리

## 설치 및 실행

### 방법 1: Docker 사용 (권장)

#### 개발 환경
```bash
# 전체 MSA 환경 실행 (게이트웨이 + 샘플 서비스들)
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

#### 프로덕션 환경
```bash
# 프로덕션용 실행
docker-compose -f docker-compose.prod.yml up --build
```

#### 개별 Docker 이미지 빌드
```bash
# 개발용
docker build -f Dockerfile.dev -t msa-gateway:dev .

# 프로덕션용
docker build -f Dockerfile -t msa-gateway:prod .
```

### 방법 2: 로컬 설치

#### 1. 의존성 설치

##### 방법 1: 자동 설치 스크립트 사용 (권장)
```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

##### 방법 2: 수동 설치
```bash
# pip 업그레이드 및 빌드 도구 설치
python -m pip install --upgrade pip setuptools wheel

# 개별 패키지 설치
pip install fastapi>=0.100.0,<0.105.0
pip install "uvicorn[standard]>=0.20.0,<0.25.0"
pip install httpx>=0.24.0,<0.26.0
pip install pydantic>=2.0.0,<3.0.0
pip install python-multipart>=0.0.5,<0.1.0
```

##### 방법 3: requirements.txt 사용
```bash
pip install -r requirements.txt
```

#### 2. 서비스 실행
```bash
# 개발 모드
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 또는 직접 실행
python app/main.py
```

#### 3. 설치 테스트
```bash
python test_installation.py
```

## Docker 명령어 가이드

```bash
# Docker 명령어 확인
chmod +x docker-commands.sh
./docker-commands.sh
```

### 주요 Docker 명령어

| 명령어 | 설명 |
|--------|------|
| `docker-compose up --build` | 개발 환경 실행 |
| `docker-compose -f docker-compose.prod.yml up --build` | 프로덕션 환경 실행 |
| `docker-compose down` | 서비스 중지 |
| `docker ps` | 실행 중인 컨테이너 확인 |
| `docker logs msa-gateway` | 게이트웨이 로그 확인 |

## 설치 문제 해결

### pip 설치 오류가 발생하는 경우:
1. **pip 업그레이드**: `python -m pip install --upgrade pip setuptools wheel`
2. **가상환경 사용**: `python -m venv venv && source venv/bin/activate` (Linux/Mac) 또는 `venv\Scripts\activate` (Windows)
3. **개별 패키지 설치**: 위의 방법 2 사용
4. **캐시 클리어**: `pip cache purge`

### 메타데이터 생성 오류 (pyproject.toml) 해결:
1. **빌드 도구 업데이트**: `pip install --upgrade setuptools wheel`
2. **패키지 버전 호환성 확인**: requirements.txt의 버전 범위 사용
3. **가상환경 재생성**: 기존 가상환경 삭제 후 새로 생성
4. **Docker 사용**: Docker를 사용하면 환경 문제 해결

### 패키지 버전 충돌이 발생하는 경우:
- `pip install --force-reinstall 패키지명` 사용
- 가상환경을 새로 만들어서 설치

### Docker 관련 문제:
- Docker Desktop이 실행 중인지 확인
- 포트 충돌 시 다른 포트 사용: `docker-compose up -p 8001:8000`
- 빌드 캐시 클리어: `docker system prune -a`

## API 엔드포인트

### 게이트웨이 정보
- `GET /` - 게이트웨이 상태 및 엔드포인트 정보
- `GET /health` - 게이트웨이 헬스 체크

### 서비스 디스커버리
- `GET /api/discovery/services` - 모든 등록된 서비스 조회
- `GET /api/discovery/services/{service_name}` - 특정 서비스 상태 조회
- `POST /api/discovery/services` - 새 서비스 등록
- `DELETE /api/discovery/services/{service_name}` - 서비스 등록 해제
- `GET /api/discovery/health` - 디스커버리 서비스 헬스 체크

### 프록시 라우팅
- `GET/POST/PUT/DELETE/PATCH /proxy/{service_name}/{path}` - 서비스로 요청 프록시
- `GET/POST/PUT/DELETE/PATCH /proxy/{service_name}` - 서비스 루트로 요청 프록시

### 사용자 서비스 (예시)
- `GET /api/users` - 사용자 목록 조회
- `GET /api/users/{user_id}` - 특정 사용자 조회
- `POST /api/users` - 사용자 생성
- `PUT /api/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/users/{user_id}` - 사용자 삭제

## 서비스 등록 예시

### 새 서비스 등록
```bash
curl -X POST "http://localhost:8000/api/discovery/services" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "my-service",
    "base_url": "http://localhost:8080",
    "health_check_url": "http://localhost:8080/health",
    "metadata": {
      "version": "1.0.0",
      "environment": "production"
    }
  }'
```

### 서비스로 요청 프록시
```bash
# 서비스의 /api/data 엔드포인트로 요청
curl -X GET "http://localhost:8000/proxy/my-service/api/data"

# POST 요청도 지원
curl -X POST "http://localhost:8000/proxy/my-service/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## 서비스 상태

게이트웨이는 등록된 모든 서비스에 대해 주기적으로 헬스 체크를 수행합니다:

- **HEALTHY**: 서비스가 정상 동작 중
- **UNHEALTHY**: 서비스에 문제가 있음
- **UNKNOWN**: 아직 헬스 체크를 수행하지 않음

## 개발 환경 설정

### 샘플 서비스 등록
게이트웨이 시작 시 다음 샘플 서비스들이 자동으로 등록됩니다:

- `user-service`: http://localhost:8001
- `product-service`: http://localhost:8002  
- `order-service`: http://localhost:8003

### 로그 확인
```bash
# 로그 레벨 설정
export LOG_LEVEL=INFO

# 애플리케이션 실행
python app/main.py
```

## 프로덕션 배포

### 환경 변수 설정
```bash
export ENVIRONMENT=production
export ALLOWED_HOSTS=your-domain.com
export ALLOWED_ORIGINS=https://your-frontend.com
```

### Docker 실행
```bash
# 이미지 빌드
docker build -t msa-gateway .

# 컨테이너 실행
docker run -p 8000:8000 msa-gateway
```

## 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| Gateway | http://localhost:8000 | 메인 게이트웨이 |
| API Docs | http://localhost:8000/docs | Swagger UI |
| User Service | http://localhost:8001 | 사용자 서비스 |
| Product Service | http://localhost:8002 | 상품 서비스 |
| Order Service | http://localhost:8003 | 주문 서비스 |

## 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   Gateway       │    │   Microservices │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Frontend  │ │───▶│ │   Proxy     │ │───▶│ │User Service │ │
│ └─────────────┘ │    │ │ Controller  │ │    │ └─────────────┘ │
│                 │    │ └─────────────┘ │    │                 │
│                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│                 │    │ │  Service    │ │    │ │Product      │ │
│                 │    │ │ Registry    │ │    │ │Service      │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│                 │    │ │ Health      │ │    │ │Order        │ │
│                 │    │ │ Checker     │ │    │ │Service      │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 라이센스

MIT License 