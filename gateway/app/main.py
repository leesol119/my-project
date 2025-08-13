"""
Gateway API 메인 파일 - 메인 라우터 역할
CORS 문제 근본 해결 버전
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import httpx
import logging
import os
import re
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

# Account Service URL (환경변수로 설정 가능)
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8003")

# Railway 환경에서는 Account Service URL을 환경변수에서 가져옴
if os.getenv("RAILWAY_ENVIRONMENT") == "true":
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "https://your-account-service-url.railway.app")

# 로컬 개발 환경에서는 Docker Compose 네트워크 사용
if os.getenv("ENVIRONMENT") == "development":
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8003")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    logger.info(f"📡 Account Service URL: {ACCOUNT_SERVICE_URL}")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for EriPotter Project - Main Router",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정 - 근본적 해결
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https:\/\/([a-z0-9-]+\.)*eripotter\.com$|^https?:\/\/localhost:(3000|3001)$|^https?:\/\/192\.168\.\d+\.\d+:(3000|3001)$",
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=False,  # 쿠키/세션 필요 시 True로 변경 (와일드카드 Origin 금지)
    max_age=86400,
)

# 요청 모델
class LoginRequest(BaseModel):
    user_id: str
    password: str

class SignUpRequest(BaseModel):
    user_id: str
    password: str
    company_id: str = None

# HTTP 클라이언트
http_client = httpx.AsyncClient(timeout=30.0)

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Gateway API - Main Router", "version": "0.1.0", "status": "running"}

@app.get("/health")
async def health():
    logger.info("🏥 헬스체크 요청 받음 - /health")
    return {
        "status": "ok",
        "service": "gateway",
        "timestamp": "2025-08-13",
        "port": 8080
    }

@app.get("/healthz")
async def healthz():
    logger.info("HEALTHZ 요청")
    return {"status": "ok"}

# CORS 프리플라이트 핸들러 - 모든 경로에 대해 OPTIONS 처리
@app.options("/{path:path}")
async def preflight_handler(path: str, request: Request):
    logger.info(f"PRELIGHT {path} origin={request.headers.get('origin')}")
    return PlainTextResponse("", status_code=200)

# 로그인 엔드포인트 - Account Service로 프록시
@app.post("/login")
async def login(request: LoginRequest, http_request: Request):
    logger.info(f"LOGIN {request.user_id} origin={http_request.headers.get('origin')}")
    
    try:
        # Account Service로 요청 전달
        response = await http_client.post(
            f"{ACCOUNT_SERVICE_URL}/login",
            json=request.dict(),
            headers={
                "Content-Type": "application/json",
                "Origin": http_request.headers.get("origin", ""),
            }
        )
        
        logger.info(f"Account Service 응답: {response.status_code}")
        
        # 응답 반환 (CORS 헤더는 미들웨어가 처리)
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
        
    except httpx.RequestError as e:
        logger.error(f"Account Service 연결 오류: {e}")
        raise HTTPException(status_code=503, detail="Account Service 연결 오류")
    except Exception as e:
        logger.error(f"로그인 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 오류")

# 회원가입 엔드포인트 - Account Service로 프록시
@app.post("/signup")
async def signup(request_data: SignUpRequest, http_request: Request):
    logger.info(f"SIGNUP {request_data.user_id} origin={http_request.headers.get('origin')}")
    
    try:
        # Account Service로 요청 전달
        response = await http_client.post(
            f"{ACCOUNT_SERVICE_URL}/signup",
            json=request_data.dict(),
            headers={
                "Content-Type": "application/json",
                "Origin": http_request.headers.get("origin", ""),
            }
        )
        
        logger.info(f"Account Service 응답: {response.status_code}")
        
        # 응답 반환 (CORS 헤더는 미들웨어가 처리)
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
        
    except httpx.RequestError as e:
        logger.error(f"Account Service 연결 오류: {e}")
        raise HTTPException(status_code=503, detail="Account Service 연결 오류")
    except Exception as e:
        logger.error(f"회원가입 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="회원가입 처리 오류")

# 기타 엔드포인트들 - Account Service로 프록시
@app.post("/user/login")
async def user_login(request: LoginRequest, http_request: Request):
    """user/login 경로로도 로그인 가능하도록"""
    return await login(request, http_request)

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    # 고정 포트 사용
    port = 8080
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
