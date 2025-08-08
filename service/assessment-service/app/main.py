"""
Assessment Service 메인 파일
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("assessment_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Assessment Service 시작")
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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.vercel.app",  # Vercel 도메인으로 변경
    ],
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
        "service": "assessment"
    }

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "assessment"}

# 라우터 등록
try:
    from app.router.main_router import router as main_router
    app.include_router(main_router, prefix="/api/v1")
except ImportError:
    logger.warning("main_router not found")

try:
    from app.router.auth_router import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth")
except ImportError:
    logger.warning("auth_router not found")

try:
    from app.router.le_router import router as le_router
    app.include_router(le_router, prefix="/api/v1/le")
except ImportError:
    logger.warning("le_router not found")

try:
    from app.router.sme_router import router as sme_router
    app.include_router(sme_router, prefix="/api/v1/sme")
except ImportError:
    logger.warning("sme_router not found")

try:
    from app.router.user_router import router as user_router
    app.include_router(user_router, prefix="/api/v1/user")
except ImportError:
    logger.warning("user_router not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
