"""
Gateway API 메인 파일 - 메인 라우터 역할
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import logging
import os
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

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.eripotter.com",
        "https://eripotter.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.0.99:3000",
        "http://192.168.0.99:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
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
async def health_check():
    logger.info("🏥 헬스체크 요청 받음")
    return {"status": "healthy!", "service": "gateway"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/health/minimal")
async def minimal_health_check():
    return {"status": "ok"}

# CORS 프리플라이트 처리
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    logger.info(f"🔄 CORS 프리플라이트 요청: {request.method} {path}")
    
    origin = request.headers.get('origin', '')
    response = JSONResponse(content={})
    
    # 허용된 도메인 체크
    allowed_domains = [
        "https://www.eripotter.com",
        "https://eripotter.com",
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    if origin in allowed_domains or origin.endswith('.vercel.app'):
        response.headers["Access-Control-Allow-Origin"] = origin
        logger.info(f"✅ 도메인 허용: {origin}")
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://www.eripotter.com"
        logger.warning(f"⚠️ 허용되지 않은 도메인: {origin}")
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    
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
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "*",
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
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "*",
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
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
