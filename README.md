# EriPotter - 마이크로서비스 아키텍처 프로젝트

## 📋 프로젝트 개요

EriPotter는 마이크로서비스 아키텍처를 기반으로 한 API 게이트웨이와 프론트엔드 애플리케이션을 포함한 전체 스택 프로젝트입니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │
│   (Next.js)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘
```

## 🚀 빠른 시작

### 개발 환경 실행

#### Windows
```bash
start-dev.bat
```

#### Linux/Mac
```bash
chmod +x start-dev.sh
./start-dev.sh
```

#### 수동 실행
```bash
docker-compose up --build -d
```

### 프로덕션 환경 실행

#### Windows
```bash
start-prod.bat
```

#### Linux/Mac
```bash
chmod +x start-prod.sh
./start-prod.sh
```

#### 수동 실행
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🌐 서비스 접속 정보

### 개발 환경
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **API 문서**: http://localhost:8080/docs


### 프로덕션 환경
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 📁 프로젝트 구조

```
eripotter/
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   ├── Dockerfile           # 개발용 Dockerfile
│   ├── Dockerfile.prod      # 프로덕션용 Dockerfile
│   └── .dockerignore
├── gateway/                  # FastAPI API 게이트웨이
│   ├── app/
│   ├── Dockerfile           # 프로덕션용 Dockerfile
│   ├── Dockerfile.dev       # 개발용 Dockerfile
│   ├── docker-compose.yml   # 게이트웨이 전용 (개발)
│   └── docker-compose.prod.yml # 게이트웨이 전용 (프로덕션)
├── docker-compose.yml       # 전체 프로젝트 (개발)
├── docker-compose.prod.yml  # 전체 프로젝트 (프로덕션)
├── start-dev.sh             # 개발 환경 실행 스크립트
├── start-prod.sh            # 프로덕션 환경 실행 스크립트
├── start-dev.bat            # Windows 개발 환경 실행
├── start-prod.bat           # Windows 프로덕션 환경 실행
└── README.md
```

## 🛠️ 주요 기능

### Frontend (Next.js)
- React 19 + TypeScript
- Tailwind CSS 스타일링
- Zustand 상태 관리
- API 게이트웨이와 통신

### API Gateway (FastAPI)
- 마이크로서비스 프록시
- 서비스 디스커버리
- 로드 밸런싱
- CORS 처리
- JSON 데이터 수신/처리



## 📝 사용법

### 1. 프론트엔드에서 데이터 전송
1. http://localhost:3000 접속
2. 입력 필드에 텍스트 입력
3. Enter 키 또는 마이크 버튼 클릭
4. JSON 데이터가 API 게이트웨이로 전송됨

### 2. API 게이트웨이 확인
1. http://localhost:8080/docs 접속 (개발)
2. http://localhost:8000/docs 접속 (프로덕션)
3. `/api/input` 엔드포인트에서 전송된 데이터 확인

### 3. 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f frontend
docker-compose logs -f gateway
```

## 🔧 관리 명령어

### 컨테이너 관리
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f [service-name]
```

### 이미지 관리
```bash
# 이미지 빌드
docker-compose build

# 이미지 강제 재빌드
docker-compose build --no-cache

# 사용하지 않는 이미지 정리
docker image prune
```

## 🐛 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8080

# 프로세스 종료
taskkill /PID [process-id] /F
```

### 컨테이너 문제
```bash
# 컨테이너 상태 확인
docker ps -a

# 컨테이너 재시작
docker-compose restart [service-name]

# 컨테이너 완전 재생성
docker-compose down
docker-compose up --build -d
```

## 📚 기술 스택

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Container**: Docker, Docker Compose
- **Database**: (필요시 추가)
- **Message Queue**: (필요시 추가)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 연락처

프로젝트 링크: [https://github.com/your-username/eripotter](https://github.com/your-username/eripotter) 