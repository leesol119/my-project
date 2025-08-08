"""
Gateway API 메인 파일
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for EriPotter Project",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://(www\.)?eripotter\.com$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# 요청 모델
class LoginRequest(BaseModel):
    user_id: str
    user_pw: str

class SignUpRequest(BaseModel):
    user_id: str
    user_pw: int
    company_id: str = None

# 전역 변수
latest_login_data = None
latest_signup_data = None

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0", "status": "running"}

@app.get("/health")
async def health_check():
    logger.info("🏥 헬스체크 요청 받음")
    return {"status": "healthy!", "service": "gateway"}

@app.get("/health/minimal")
async def minimal_health_check():
    return {"status": "ok"}

# CORS 프리플라이트 처리
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    logger.info(f"🔄 CORS 프리플라이트 요청: {request.method} {path}")
    
    origin = request.headers.get('origin', '')
    response = JSONResponse(status_code=200, content={})
    
    # 허용된 도메인 체크
    allowed_domains = [
        "https://www.eripotter.com",
        "https://www.eripotter.com/",
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

# 로그인 엔드포인트
@app.post("/login")
async def login(request: LoginRequest):
    global latest_login_data
    latest_login_data = request.dict()
    logger.info(f"로그인 요청 받음: {latest_login_data}")
    return {"result": "로그인 성공!", "received_data": latest_login_data}

# 회원가입 엔드포인트
@app.post("/signup")
async def signup(request_data: SignUpRequest, request: Request):
    global latest_signup_data
    latest_signup_data = request_data.dict()
    logger.info(f"🚀 회원가입 요청 받음: {latest_signup_data}")
    
    origin = request.headers.get('origin', '')
    response = JSONResponse(content={"result": "회원가입 성공!", "received_data": latest_signup_data})
    
    # CORS 헤더 설정
    allowed_domains = [
        "https://www.eripotter.com",
        "https://www.eripotter.com/",
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    if origin in allowed_domains or origin.endswith('.vercel.app'):
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://www.eripotter.com"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# 데이터 확인 엔드포인트
@app.get("/login")
async def get_latest_login():
    global latest_login_data
    if latest_login_data:
        return latest_login_data
    return {"message": "아직 로그인 데이터가 없습니다"}

@app.get("/signup")
async def get_latest_signup():
    global latest_signup_data
    if latest_signup_data:
        return latest_signup_data
    return {"message": "아직 회원가입 데이터가 없습니다"}

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
