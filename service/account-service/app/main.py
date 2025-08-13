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
    title="Account Service API",
    description="Account 서비스 - 로그인/회원가입 담당",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eripotter.com",      # 프로덕션 도메인
        "https://www.eripotter.com",  # www 서브도메인
        "http://localhost:3000",      # 개발 환경
        "http://localhost:3001",      # 개발 환경
        "http://192.168.0.99:3000",   # 로컬 네트워크
        "http://192.168.0.99:3001",   # 로컬 네트워크
    ],
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델
class LoginRequest(BaseModel):
    user_id: str
    password: str

class SignUpRequest(BaseModel):
    user_id: str
    password: str
    company_id: str = None

# 라우터 포함 (존재하는 것만)
# app.include_router(director_router)
# app.include_router(executive_router)
# app.include_router(manager_router)
# app.include_router(supervisor_router)
# app.include_router(worker_router)
app.include_router(auth_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {request.client.host})")
    try:
        response = await call_next(request)
        logger.info(f"📤 응답: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 요청 처리 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Account Service API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy!", "service": "account"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# 로그인 엔드포인트
@app.post("/login")
async def login(request: LoginRequest, http_request: Request):
    logger.info(f"🔐 로그인 요청 받음: {request.user_id}")
    
    try:
        # 여기에 실제 로그인 로직 구현
        # 예시: 데이터베이스 조회, 비밀번호 검증 등
        
        # 임시 응답 (실제로는 데이터베이스 조회 후 결과 반환)
        if request.user_id and request.password:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "로그인 성공",
                    "user_id": request.user_id,
                    "token": "sample_token_12345"  # 실제로는 JWT 토큰 생성
                },
                headers={
                    "Access-Control-Allow-Origin": http_request.headers.get("origin", "https://www.eripotter.com"),
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                    "Access-Control-Allow-Headers": "*",
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
    logger.info(f"🚀 회원가입 요청 받음: {request_data.user_id}")
    
    try:
        # 여기에 실제 회원가입 로직 구현
        # 예시: 데이터베이스 저장, 중복 확인 등
        
        # 임시 응답 (실제로는 데이터베이스 저장 후 결과 반환)
        if request_data.user_id and request_data.password:
            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "회원가입 성공",
                    "user_id": request_data.user_id,
                    "company_id": request_data.company_id
                },
                headers={
                    "Access-Control-Allow-Origin": http_request.headers.get("origin", "https://www.eripotter.com"),
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        else:
            raise HTTPException(status_code=400, detail="사용자 ID와 비밀번호가 필요합니다")
            
    except Exception as e:
        logger.error(f"❌ 회원가입 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="회원가입 처리 오류")

# Railway 환경에서 실행
if __name__ == "__main__":
    # 고정 포트 사용
    port = 8003
    logger.info(f"🚀 Account Service 시작 - 포트: {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )