"""
Account 서비스 메인 애플리케이션 진입점
"""
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# from app.router.director_router import director_router
# from app.router.executive_router import executive_router
# from app.router.manager_router import manager_router
# from app.router.supervisor_router import supervisor_router
# from app.router.worker_router import worker_router
from app.router.user_router import auth_router
import uvicorn
import logging
import traceback
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("account_service")
 
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

app = FastAPI(
    title="Account Service",
    description="사용자 인증 및 계정 관리 서비스",
    version="1.0.0"
)

# CORS 설정 - 내부 통신 전제 (Gateway에서만 CORS 처리)
# 선택지 1: CORS 완전 비활성화 (권장)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[],  # 빈 리스트로 모든 Origin 차단
#     allow_credentials=False,
#     allow_methods=[],
#     allow_headers=[],
# )

# 선택지 2: 최소 CORS 설정 (Gateway와 내부 통신만 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://my-project-production-0a50.up.railway.app",
        "https://localhost:8080",    # 로컬 개발
        "https://127.0.0.1:8080",    # 로컬 개발
    ],
    allow_credentials=False,        # 내부 통신이므로 credentials 불필요
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic 모델
class LoginRequest(BaseModel):
    user_id: str
    password: str

class SignUpRequest(BaseModel):
    user_id: str
    password: str
    company_id: str | None = None

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Account Service",
        "version": "1.0.0",
        "status": "running"
    }

# 헬스체크 엔드포인트
@app.get("/health")
async def health():
    return {"status": "ok", "service": "account"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "account"}

# 핑 테스트
@app.get("/ping")
async def ping():
    return {"message": "pong", "service": "account"}

# 로그인 엔드포인트
@app.post("/login")
async def login(request: LoginRequest, http_request: Request):
    logger.info(f"🔐 LOGIN {request.user_id} origin={http_request.headers.get('origin')}")
    try:
        if request.user_id and request.password:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "로그인 성공",
                    "user_id": request.user_id,
                    "token": "sample_token_12345"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="사용자 ID와 비밀번호가 필요합니다")
    except Exception as e:
        logger.error(f"❌ 로그인 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 오류")

# 회원가입 엔드포인트
@app.post("/signup")
async def signup(request_data: SignUpRequest, http_request: Request):
    logger.info(f"📝 SIGNUP {request_data.user_id} origin={http_request.headers.get('origin')}")
    try:
        if request_data.user_id and request_data.password:
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "회원가입 성공",
                    "user_id": request_data.user_id,
                    "company_id": request_data.company_id
                }
            )
        else:
            raise HTTPException(status_code=400, detail="사용자 ID와 비밀번호가 필요합니다")
    except Exception as e:
        logger.error(f"❌ 회원가입 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="회원가입 처리 오류")

# 사용자 프로필 엔드포인트 (인증 필요)
@app.get("/profile")
async def get_profile(http_request: Request):
    auth_header = http_request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    logger.info(f"👤 PROFILE 조회 origin={http_request.headers.get('origin')}")
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "user_id": "sample_user",
            "email": "user@example.com",
            "company_id": "sample_company"
        }
    )

# 로그아웃 엔드포인트 (인증 필요)
@app.post("/logout")
async def logout(http_request: Request):
    auth_header = http_request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    logger.info(f"🚪 LOGOUT origin={http_request.headers.get('origin')}")
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "로그아웃 성공"
        }
    )

# 서비스 정보
@app.get("/info")
async def service_info():
    return {
        "service": "account",
        "version": "1.0.0",
        "endpoints": [
            "/login",
            "/signup", 
            "/profile",
            "/logout",
            "/health",
            "/ping"
        ]
    }

# Railway 환경에서 실행
if __name__ == "__main__":
    # 고정 포트 사용
    port = 8003
    logger.info(f"🚀 Account Service 시작 - 포트: {port}")
    logger.info(f"📡 서비스 URL: http://0.0.0.0:{port}")
    logger.info(f"🔍 헬스체크 URL: http://0.0.0.0:{port}/healthz")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )