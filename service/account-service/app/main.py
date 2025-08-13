"""
Account 서비스 메인 애플리케이션 진입점
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("account_service")

app = FastAPI(
    title="Account Service",
    description="사용자 인증 및 계정 관리 서비스",
    version="1.0.0"
)

# CORS 설정 - Gateway와 내부 통신만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://my-project-production-0a50.up.railway.app",  # Gateway URL
        "http://localhost:8080",    # 로컬 개발
        "http://127.0.0.1:8080",    # 로컬 개발
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
    """MVC 구조: Account Service에서 로그인 처리"""
    logger.info(f"🔐 Account Service 로그인 요청 수신: user_id={request.user_id}, origin={http_request.headers.get('origin')}")
    
    try:
        # 1. 입력값 검증
        logger.info(f"📋 로그인 입력값 검증: user_id={request.user_id}, password_length={len(request.password) if request.password else 0}")
        
        if not request.user_id or not request.password:
            logger.warning(f"❌ 로그인 실패: 필수 입력값 누락 - user_id={request.user_id}, password_provided={bool(request.password)}")
            raise HTTPException(status_code=400, detail="사용자 ID와 비밀번호가 필요합니다")
        
        # 2. 로그인 처리 (실제로는 데이터베이스 확인)
        logger.info(f"🔍 사용자 인증 처리: {request.user_id}")
        
        # 3. 성공 응답
        logger.info(f"✅ 로그인 성공: {request.user_id}")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "로그인 성공 (Account Service)",
                "user_id": request.user_id,
                "token": f"account_token_{request.user_id}_{int(time.time())}",
                "service": "account-service"
            }
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        logger.error(f"❌ Account Service 로그인 처리 오류: {e}")
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
    port = 8003
    logger.info(f"🚀 Account Service 시작 - 포트: {port}")
    
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )