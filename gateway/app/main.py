"""
Gateway API 메인 파일 - 서비스 디스커버리 역할
CORS 문제 근본 해결 버전
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx
import logging
import os
import re
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

# 서비스 URL 설정
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8003")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")

# Railway 환경에서는 서비스 URL을 환경변수에서 가져옴
if os.getenv("RAILWAY_ENVIRONMENT") == "true":
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "https://your-account-service-url.railway.app")
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "https://your-chatbot-service-url.railway.app")
    logger.info(f"🚀 Railway 환경 감지")

# 로컬 개발 환경에서는 Docker Compose 네트워크 사용
if os.getenv("ENVIRONMENT") == "development":
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8003")
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8004")
    logger.info(f"🔧 개발 환경 감지")

logger.info(f"📡 Account Service URL: {ACCOUNT_SERVICE_URL}")
logger.info(f"📡 Chatbot Service URL: {CHATBOT_SERVICE_URL}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    logger.info(f"📡 Account Service URL: {ACCOUNT_SERVICE_URL}")
    logger.info(f"📡 Chatbot Service URL: {CHATBOT_SERVICE_URL}")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for EriPotter Project - Service Discovery",
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

# HTTP 클라이언트
http_client = httpx.AsyncClient(timeout=30.0)

# 범용 프록시 함수
async def _proxy(request: Request, service_url: str, path: str):
    """서비스로 요청을 프록시하는 범용 함수"""
    method = request.method
    target_url = f"{service_url}/{path.lstrip('/')}"
    
    logger.info(f"PROXY {method} {target_url} origin={request.headers.get('origin')}")
    
    try:
        # 요청 본문 읽기
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()
        
        # 헤더 준비
        headers = dict(request.headers)
        headers.pop("host", None)  # host 헤더 제거
        
        # 서비스로 요청 전송
        response = await http_client.request(
            method=method,
            url=target_url,
            json=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None,
            headers=headers,
            params=request.query_params
        )
        
        logger.info(f"Service 응답: {response.status_code}")
        
        # 응답 반환
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            headers=dict(response.headers)
        )
        
    except httpx.RequestError as e:
        logger.error(f"Service 연결 오류: {e}")
        logger.error(f"Service URL: {service_url}")
        raise HTTPException(status_code=503, detail=f"Service 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"프록시 오류: {e}")
        raise HTTPException(status_code=500, detail="프록시 오류")

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Gateway API - Service Discovery", "version": "0.1.0", "status": "running"}

@app.get("/healthz")
async def healthz():
    logger.info("HEALTHZ 요청")
    return {"status": "ok"}

@app.get("/test-account-service")
async def test_account_service():
    logger.info("Account Service 연결 테스트")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ACCOUNT_SERVICE_URL}/health")
            logger.info(f"Account Service 응답: {response.status_code}")
            return {
                "status": "ok",
                "account_service_url": ACCOUNT_SERVICE_URL,
                "account_service_status": response.status_code,
                "account_service_response": response.json()
            }
    except Exception as e:
        logger.error(f"Account Service 연결 실패: {e}")
        return {
            "status": "error",
            "account_service_url": ACCOUNT_SERVICE_URL,
            "error": str(e)
        }

# CORS 프리플라이트 핸들러 - 모든 경로에 대해 OPTIONS 처리
@app.options("/{path:path}")
async def preflight_handler(path: str, request: Request):
    logger.info(f"PRELIGHT {path} origin={request.headers.get('origin')}")
    return PlainTextResponse("", status_code=200)

# ---- account-service 프록시 ----
@app.api_route("/api/account", methods=["GET","POST","PUT","PATCH","DELETE"])
async def account_root(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/")

@app.api_route("/api/account/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def account_any(path: str, request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, path)

# ---- chatbot-service 프록시 ----
@app.api_route("/api/chatbot", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_root(request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, "/")

@app.api_route("/api/chatbot/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def chatbot_any(path: str, request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, path)

# 기존 경로 호환성 유지 (점진적 마이그레이션용)
@app.post("/login")
async def login_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/login")

@app.post("/signup")
async def signup_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/signup")

@app.post("/user/login")
async def user_login_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/login")

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    # 고정 포트 사용
    port = 8080
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
