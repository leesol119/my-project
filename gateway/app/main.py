"""
Gateway API 메인 파일 - 서비스 디스커버리 역할
CORS 문제 근본 해결 버전
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse
import httpx
import logging
import os
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Service Discovery Gateway",
    description="마이크로서비스 프록시 및 서비스 디스커버리",
    version="1.0.0"
)

# 환경 변수
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8003")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8004")

logger.info(f"🔧 ACCOUNT_SERVICE_URL: {ACCOUNT_SERVICE_URL}")
logger.info(f"🔧 CHATBOT_SERVICE_URL: {CHATBOT_SERVICE_URL}")

# HTTP 클라이언트 설정
http_client = httpx.AsyncClient(timeout=30.0)

# CORS: 운영 도메인 및 서브도메인 허용 (+개발용)
WHITELIST = {
    "https://sme.eripotter.com",
    "https://www.sme.eripotter.com",              # www 서브도메인도 허용
    "http://localhost:3000", 
    "http://localhost:5173",                      # 로컬 개발
    "http://127.0.0.1:3000",
    "http://frontend:3000",                       # Docker 네트워크
    # "https://sme-eripotter-com.vercel.app",     # Vercel 프리뷰를 쓰면 주석 해제
}

# 서브도메인 허용을 위한 정규식 패턴
ALLOWED_DOMAINS = [
    r"^https://([a-z0-9-]+\.)*sme\.eripotter\.com$",  # sme.eripotter.com의 모든 서브도메인
    r"^https://([a-z0-9-]+\.)*eripotter\.com$",       # eripotter.com의 모든 서브도메인
    r"^http://localhost:\d+$",                        # localhost의 모든 포트
    r"^http://127\.0\.0\.1:\d+$",                     # 127.0.0.1의 모든 포트
    r"^http://192\.168\.\d+\.\d+:\d+$",               # 로컬 네트워크의 모든 IP와 포트
]

# 미들웨어(기본 방어막) - allow_origins는 넓게 두되 credentials 고려
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(WHITELIST),
    allow_origin_regex=r"^https://([a-z0-9-]+\.)*sme\.eripotter\.com$|^https://([a-z0-9-]+\.)*eripotter\.com$|^http://localhost:\d+$|^http://127\.0\.0\.1:\d+$|^http://192\.168\.\d+\.\d+:\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

def cors_headers_for(request: Request):
    """요청 Origin이 허용 목록에 있으면 해당 Origin을 그대로 반환."""
    import re
    
    origin = request.headers.get("origin")
    if not origin:
        return {}
    
    # 1. WHITELIST에 직접 있는지 확인
    if origin in WHITELIST:
        logger.info(f"✅ WHITELIST 매치: {origin}")
        return {
            "Access-Control-Allow-Origin": origin,
            "Vary": "Origin",  # 캐시 안정성
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
        }
    
    # 2. 정규식 패턴으로 서브도메인 확인
    for pattern in ALLOWED_DOMAINS:
        if re.match(pattern, origin):
            logger.info(f"✅ 정규식 매치: {origin} (패턴: {pattern})")
            return {
                "Access-Control-Allow-Origin": origin,
                "Vary": "Origin",  # 캐시 안정성
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
            }
    
    # 허용되지 않은 Origin
    logger.warning(f"🚫 허용되지 않은 Origin: {origin}")
    return {}

# 인증 미들웨어 (2번째 실행 - 역순 적용)
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
        # OPTIONS 요청은 무조건 통과 (preflight 처리)
        if request.method == "OPTIONS":
            logger.info(f"🔓 PREFLIGHT 통과: {request.url.path}")
            return await call_next(request)
        
        # 인증이 필요한 엔드포인트 체크
        auth_required_paths = ["/api/account/profile", "/api/account/logout"]
        if any(request.url.path.startswith(path) for path in auth_required_paths):
            auth_header = request.headers.get("authorization")
            if not auth_header:
                logger.warning(f"🚫 인증 필요 경로에서 Authorization 헤더 누락: {request.url.path}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization header required"}
                )
        
        logger.info(f"🔐 인증 미들웨어 통과: {request.method} {request.url.path}")
        return await call_next(request)

app.add_middleware(AuthMiddleware)

# 프리플라이트 핸들러 - 모든 경로에 대한 OPTIONS 요청 처리
@app.options("/{path:path}")
async def preflight_handler(path: str, request: Request):
    origin = request.headers.get("origin")
    request_method = request.headers.get("access-control-request-method", "*")
    request_headers = request.headers.get("access-control-request-headers", "*")
    
    logger.info(f"🔄 PREFLIGHT 처리: {path} origin={origin} method={request_method} headers={request_headers}")
    
    # CORS 헤더 생성
    cors_headers = cors_headers_for(request)
    
    if not cors_headers:
        logger.warning(f"🚫 허용되지 않은 Origin: {origin}")
        return Response(status_code=403)
    
    return Response(
        status_code=200,
        headers=cors_headers
    )

# 범용 프록시 함수
async def _proxy(request: Request, service_url: str, path: str):
    """서비스로 요청을 프록시하는 범용 함수"""
    method = request.method
    target_url = f"{service_url}/{path.lstrip('/')}"
    
    logger.info(f"🌐 PROXY {method} {target_url} origin={request.headers.get('origin')}")
    logger.info(f"🔧 Service URL: {service_url}")
    
    try:
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                logger.info(f"📦 Request body: {body}")
            except Exception as e:
                logger.warning(f"⚠️ JSON 파싱 실패, 바이너리로 처리: {e}")
                body = await request.body()
        
        # hop-by-hop 헤더 제거 (프록시 응답에서 제거됨)
        headers = dict(request.headers)
        hop_by_hop_headers = [
            "connection", "keep-alive", "proxy-authenticate", 
            "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
        ]
        for header in hop_by_hop_headers:
            headers.pop(header, None)
        headers.pop("host", None)
        
        logger.info(f"📋 Request headers: {headers}")
        
        logger.info(f"🚀 서비스로 요청 전송 중: {target_url}")
        response = await http_client.request(
            method=method,
            url=target_url,
            json=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None,
            headers=headers,
            params=request.query_params
        )
        
        logger.info(f"✅ Service 응답: {response.status_code}")
        logger.info(f"📋 Response headers: {dict(response.headers)}")
        
        # 프록시 응답 헤더에서 hop-by-hop 헤더 제거
        response_headers = dict(response.headers)
        for header in hop_by_hop_headers:
            response_headers.pop(header, None)
        
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            headers=response_headers
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Service 연결 오류: {e}")
        logger.error(f"🔧 Service URL: {service_url}")
        logger.error(f"🎯 Target URL: {target_url}")
        logger.error(f"🔍 Error type: {type(e)}")
        raise HTTPException(status_code=503, detail=f"Service 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"❌ 프록시 오류: {e}")
        logger.error(f"🔍 Error type: {type(e)}")
        logger.error(f"📝 Error details: {str(e)}")
        raise HTTPException(status_code=500, detail="프록시 오류")

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

# 헬스체크 엔드포인트
@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "gateway"}

# Account Service 연결 테스트
@app.get("/test-account-service")
async def test_account_service():
    try:
        response = await http_client.get(f"{ACCOUNT_SERVICE_URL}/health")
        logger.info(f"✅ Account Service 연결 성공: {response.status_code}")
        return {
            "status": "success",
            "account_service": "connected",
            "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        }
    except Exception as e:
        logger.error(f"❌ Account Service 연결 실패: {e}")
        return {
            "status": "error",
            "account_service": "disconnected",
            "error": str(e)
        }

# favicon.ico 처리
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Service Discovery Gateway",
        "version": "1.0.0",
        "services": {
            "account": ACCOUNT_SERVICE_URL,
            "chatbot": CHATBOT_SERVICE_URL
        }
    }

# 애플리케이션 종료 시 HTTP 클라이언트 정리
@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    logger.info("🔌 HTTP 클라이언트 정리 완료")
