"""
Assessment Service 메인 파일
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys
import psutil
import time
from contextlib import asynccontextmanager
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("assessment_service")

# 서비스 시작 시간 기록
start_time = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global start_time
    start_time = time.time()
    logger.info("🚀 Assessment Service 시작")
    logger.info(f"📊 시스템 정보: CPU 코어 {psutil.cpu_count()}, 메모리 {round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2)}GB")
    logger.info("✅ 헬스체크 엔드포인트 준비됨: /health, /health/simple, /health/minimal")
    yield
    logger.info("🛑 Assessment Service 종료")

app = FastAPI(
    title="Assessment Service",
    description="Assessment Service for EriPotter Project",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Railway에서는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 루트 경로
@app.get("/")
async def root():
    return {
        "message": "Assessment Service", 
        "version": "0.1.0", 
        "status": "running",
        "service": "assessment",
        "timestamp": datetime.now().isoformat()
    }

# 개선된 헬스 체크
@app.get("/health")
async def health_check():
    """간단하고 빠른 헬스 체크 엔드포인트"""
    try:
        # 기본 시스템 정보만 빠르게 확인
        uptime = time.time() - start_time if start_time else 0
        memory_info = psutil.virtual_memory()
        
        # 서비스 상태 확인 (간단한 버전)
        health_status = {
            "status": "healthy",
            "service": "assessment",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": format_uptime(uptime),
            "system": {
                "memory_percent": memory_info.percent,
                "memory_available_mb": round(memory_info.available / 1024 / 1024, 2)
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# 간단한 헬스 체크 (기존 호환성 유지)
@app.get("/health/simple")
async def simple_health_check():
    """간단한 헬스 체크 (기존 호환성용)"""
    return {"status": "healthy", "service": "assessment"}

# 최소한의 헬스 체크 (Docker용)
@app.get("/health/minimal")
async def minimal_health_check():
    """최소한의 헬스 체크 (Docker 헬스체크용)"""
    return {"status": "ok"}

def format_uptime(seconds):
    """업타임을 사람이 읽기 쉬운 형태로 변환"""
    if seconds < 60:
        return f"{int(seconds)}초"
    elif seconds < 3600:
        return f"{int(seconds // 60)}분 {int(seconds % 60)}초"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}시간 {minutes}분"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}일 {hours}시간"

# 향후 확장을 위한 플레이스홀더 함수들
async def check_database_connection():
    """데이터베이스 연결 상태 확인 (향후 구현)"""
    return {
        "status": "healthy",
        "message": "Database connection OK (placeholder)",
        "timestamp": datetime.now().isoformat()
    }

async def check_external_services():
    """외부 서비스 연결 상태 확인 (향후 구현)"""
    return {
        "status": "healthy", 
        "message": "External services OK (placeholder)",
        "timestamp": datetime.now().isoformat()
    }

# 라우터 등록 (안전하게)
try:
    from app.router.main_router import router as main_router
    app.include_router(main_router, prefix="/api/v1")
    logger.info("✅ main_router 등록됨")
except ImportError as e:
    logger.warning(f"main_router not found: {e}")

try:
    from app.router.auth_router import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth")
    logger.info("✅ auth_router 등록됨")
except ImportError as e:
    logger.warning(f"auth_router not found: {e}")

try:
    from app.router.le_router import router as le_router
    app.include_router(le_router, prefix="/api/v1/le")
    logger.info("✅ le_router 등록됨")
except ImportError as e:
    logger.warning(f"le_router not found: {e}")

try:
    from app.router.sme_router import router as sme_router
    app.include_router(sme_router, prefix="/api/v1/sme")
    logger.info("✅ sme_router 등록됨")
except ImportError as e:
    logger.warning(f"sme_router not found: {e}")

try:
    from app.router.user_router import router as user_router
    app.include_router(user_router, prefix="/api/v1/user")
    logger.info("✅ user_router 등록됨")
except ImportError as e:
    logger.warning(f"user_router not found: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 서버 시작: 포트 {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
