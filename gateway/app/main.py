"""
Gateway API 메인 파일 - 메인 라우터 역할
CORS 문제 완전 해결 버전
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# CORS 미들웨어 설정 - 완전한 CORS 해결
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(.*\.)?eripotter\.com|https?://localhost:(3000|3001)|https?://192\.168\.\d+\.\d+:(3000|3001)",
    allow_credentials=False,  # 쿠키 사용 시 True로 변경
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24시간 캐시
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
    logger.info("🏥 헬스체크 요청 받음 - /healthz")
    return {"status": "ok", "service": "gateway", "timestamp": "2025-08-13"}

# CORS 프리플라이트 핸들러 - 모든 경로에 대해 OPTIONS 처리
@app.options("/{path:path}")
async def preflight_handler(request: Request, path: str):
    logger.info(f"🔄 CORS 프리플라이트 요청: {request.method} /{path}")
    
    origin = request.headers.get('origin', '')
    logger.info(f"📡 Origin: {origin}")
    
    # eripotter.com 도메인 또는 로컬 개발 환경 허용
    allowed_pattern = r"https?://(.*\.)?eripotter\.com|https?://localhost:(3000|3001)|https?://192\.168\.\d+\.\d+:(3000|3001)"
    
    if re.match(allowed_pattern, origin):
        logger.info(f"✅ Origin 허용: {origin}")
        response = JSONResponse(
            content={"message": "CORS preflight successful"},
            status_code=200
        )
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        logger.warning(f"⚠️ 허용되지 않은 Origin: {origin}")
        response = JSONResponse(
            content={"message": "CORS preflight failed"},
            status_code=200
        )
        response.headers["Access-Control-Allow-Origin"] = "https://www.eripotter.com"
    
    # CORS 헤더 설정
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    
    # credentials 관련 헤더 (allow_credentials=False이므로 제외)
    # response.headers["Access-Control-Allow-Credentials"] = "false"
    
    logger.info(f"📤 CORS 헤더 설정 완료: {dict(response.headers)}")
    return response

# 로그인 엔드포인트 - Account Service로 프록시
@app.post("/login")
async def login(request: LoginRequest, http_request: Request):
    logger.info(f"🔐 로그인 요청 받음: {request.user_id}")
    
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
        
        logger.info(f"📤 Account Service 응답: {response.status_code}")
        
        # 응답 반환
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers={
                "Access-Control-Allow-Origin": http_request.headers.get("origin", "https://www.eripotter.com"),
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "*",
            }
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Account Service 연결 오류: {e}")
        raise HTTPException(status_code=503, detail="Account Service 연결 오류")
    except Exception as e:
        logger.error(f"❌ 로그인 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 오류")

# 회원가입 엔드포인트 - Account Service로 프록시
@app.post("/signup")
async def signup(request_data: SignUpRequest, http_request: Request):
    logger.info(f"🚀 회원가입 요청 받음: {request_data.user_id}")
    
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
        
        logger.info(f"📤 Account Service 응답: {response.status_code}")
        
        # 응답 반환
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers={
                "Access-Control-Allow-Origin": http_request.headers.get("origin", "https://www.eripotter.com"),
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "*",
            }
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Account Service 연결 오류: {e}")
        raise HTTPException(status_code=503, detail="Account Service 연결 오류")
    except Exception as e:
        logger.error(f"❌ 회원가입 처리 오류: {e}")
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
