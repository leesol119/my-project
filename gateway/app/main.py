# main.py (gateway) — CORS 보강 버전
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse
import httpx
import logging
import os
import time
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(
    title="MSA API Gateway",
    description="마이크로서비스 프록시 및 서비스 디스커버리",
    version="1.0.0"
)

# ===== CORS 설정 =====
WHITELIST = {
    "https://sme.eripotter.com",
    "https://www.sme.eripotter.com",              # sme 서브도메인
    "https://eripotter.com",                      # 메인 도메인
    "https://www.eripotter.com",                  # www 메인 도메인
    "https://my-project-production-0a50.up.railway.app",  # Railway 배포
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
    r"^https://([a-z0-9-]+\.)*up\.railway\.app$",     # Railway의 모든 서브도메인
    r"^http://localhost:\d+$",                        # localhost의 모든 포트
    r"^http://127\.0\.0\.1:\d+$",                     # 127.0.0.1의 모든 포트
    r"^http://192\.168\.\d+\.\d+:\d+$",               # 로컬 네트워크의 모든 IP와 포트
]

# 미들웨어(기본 방어막) - allow_origins는 넓게 두되 credentials 고려
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(WHITELIST),
    allow_origin_regex=r"^https://([a-z0-9-]+\.)*sme\.eripotter\.com$|^https://([a-z0-9-]+\.)*eripotter\.com$|^https://([a-z0-9-]+\.)*up\.railway\.app$|^http://localhost:\d+$|^http://127\.0\.0\.1:\d+$|^http://192\.168\.\d+\.\d+:\d+$",
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

# 환경 변수
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8006")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8001")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "20"))

logger.info(f"🔧 ACCOUNT_SERVICE_URL: {ACCOUNT_SERVICE_URL}")
logger.info(f"🔧 CHATBOT_SERVICE_URL: {CHATBOT_SERVICE_URL}")

# 헬스체크 엔드포인트
@app.get("/health")
async def health(): 
    return {"status": "healthy", "service": "gateway"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "gateway"}

# CORS preflight 직접 처리
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """CORS preflight 직접 처리(필요 시)."""
    origin = request.headers.get("origin")
    request_method = request.headers.get("access-control-request-method", "*")
    request_headers = request.headers.get("access-control-request-headers", "*")
    
    logger.info(f"🔄 PREFLIGHT 처리: {path} origin={origin} method={request_method} headers={request_headers}")
    
    cors_headers = cors_headers_for(request)
    if not cors_headers:
        logger.warning(f"🚫 허용되지 않은 Origin: {origin}")
        return Response(status_code=403)
    
    return Response(status_code=204, headers=cors_headers)

# ---- 단일 프록시 유틸 ----
async def _proxy(request: Request, upstream_base: str, rest: str):
    url = upstream_base.rstrip("/") + "/" + rest.lstrip("/")
    logger.info(f"🔗 프록시 요청: {request.method} {request.url.path} -> {url}")

    # 원본 요청 복제
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # hop-by-hop 헤더 제거
    hop_by_hop_headers = [
        "connection", "keep-alive", "proxy-authenticate", 
        "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
    ]
    for header in hop_by_hop_headers:
        headers.pop(header, None)
    
    body = await request.body()
    params = dict(request.query_params)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            upstream = await client.request(
                request.method, url, params=params, content=body, headers=headers
            )
            logger.info(f"✅ 프록시 응답: {upstream.status_code} {url}")
    except httpx.HTTPError as e:
        logger.error(f"❌ 프록시 HTTP 오류: {e} {url}")
        # 예외를 다시 발생시켜서 fallback 로직이 실행되도록 함
        raise e
    except Exception as e:
        logger.error(f"❌ 프록시 일반 오류: {e} {url}")
        # 예외를 다시 발생시켜서 fallback 로직이 실행되도록 함
        raise e

    # 업스트림 응답 전달
    passthrough = {}
    for k, v in upstream.headers.items():
        lk = k.lower()
        if lk in ("content-type", "set-cookie", "cache-control"):
            passthrough[k] = v

    # CORS 헤더를 명시적으로 덮어쓴다(항상 부착)
    passthrough.update(cors_headers_for(request))

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=passthrough,
        media_type=upstream.headers.get("content-type"),
    )

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
    """MVC 구조: Gateway에서 로그인 요청을 받아서 Account Service로 전달"""
    try:
        # 1. 요청 본문 읽기
        body = await request.body()
        logger.info(f"🔐 Gateway 로그인 요청 수신: {body.decode()}")
        
        # 2. Account Service로 프록시 요청 시도
        try:
            logger.info(f"🔄 Account Service로 로그인 요청 전달 시도: {ACCOUNT_SERVICE_URL}/login")
            response = await _proxy(request, ACCOUNT_SERVICE_URL, "/login")
            logger.info(f"✅ Account Service 로그인 응답 성공: {response.status_code}")
            return response
            
        except Exception as proxy_error:
            logger.warning(f"⚠️ Account Service 연결 실패, Gateway 직접 처리로 전환: {proxy_error}")
            logger.info(f"🔄 Gateway 직접 로그인 처리 시작")
            direct_response = await direct_login(request)
            logger.info(f"✅ Gateway 직접 로그인 처리 완료: {direct_response.status_code}")
            return direct_response
        
    except Exception as e:
        logger.error(f"❌ Gateway 로그인 처리 중 예상치 못한 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "로그인 처리 중 오류가 발생했습니다",
                "error": str(e)
            },
            headers=cors_headers_for(request)
        )

async def direct_login(request: Request):
    """Account Service가 없을 때 Gateway에서 직접 로그인 처리"""
    try:
        logger.info(f"🔐 Gateway 직접 로그인 처리 시작")
        
        # 요청 본문을 다시 읽기 (이미 읽었을 수 있으므로)
        body = await request.body()
        logger.info(f"📋 요청 본문 읽기 완료: {body.decode()}")
        
        # JSON 파싱
        import json
        body_data = json.loads(body.decode())
        user_id = body_data.get("user_id")
        password = body_data.get("user_pw")  # frontend에서 user_pw로 보내고 있음
        
        logger.info(f"🔍 파싱된 데이터: user_id={user_id}, password_provided={bool(password)}")
        
        # 간단한 검증 (실제로는 데이터베이스 확인 필요)
        if user_id and password:
            logger.info(f"✅ Gateway 직접 로그인 성공: {user_id}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "로그인 성공 (Gateway 직접 처리)",
                    "user_id": user_id,
                    "token": f"gateway_token_{user_id}_{int(time.time())}",
                    "service": "gateway"
                },
                headers=cors_headers_for(request)
            )
        else:
            logger.warning(f"❌ Gateway 직접 로그인 실패: 필수 입력값 누락 - user_id={user_id}, password_provided={bool(password)}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "사용자 ID와 비밀번호가 필요합니다"
                },
                headers=cors_headers_for(request)
            )
    except json.JSONDecodeError as e:
        logger.error(f"❌ Gateway 직접 로그인 JSON 파싱 오류: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "잘못된 JSON 형식입니다"
            },
            headers=cors_headers_for(request)
        )
    except Exception as e:
        logger.error(f"❌ Gateway 직접 로그인 처리 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "로그인 처리 오류"
            },
            headers=cors_headers_for(request)
        )

@app.post("/signup")
async def signup_proxy(request: Request):
    """MVC 구조: Gateway에서 회원가입 요청을 받아서 Account Service로 전달"""
    try:
        # 1. 요청 본문 읽기
        body = await request.body()
        logger.info(f"📝 Gateway 회원가입 요청 수신: {body.decode()}")
        
        # 2. Account Service로 프록시 요청
        logger.info(f"🔄 Account Service로 회원가입 요청 전달: {ACCOUNT_SERVICE_URL}/signup")
        response = await _proxy(request, ACCOUNT_SERVICE_URL, "/signup")
        
        # 3. 응답 로그
        logger.info(f"✅ Account Service 회원가입 응답: {response.status_code}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Gateway 회원가입 처리 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "회원가입 처리 중 오류가 발생했습니다",
                "error": str(e)
            },
            headers=cors_headers_for(request)
        )

@app.post("/user/login")
async def user_login_proxy(request: Request):
    """MVC 구조: Gateway에서 사용자 로그인 요청을 받아서 Account Service로 전달"""
    try:
        # 1. 요청 본문 읽기
        body = await request.body()
        logger.info(f"👤 Gateway 사용자 로그인 요청 수신: {body.decode()}")
        
        # 2. Account Service로 프록시 요청
        logger.info(f"🔄 Account Service로 사용자 로그인 요청 전달: {ACCOUNT_SERVICE_URL}/login")
        response = await _proxy(request, ACCOUNT_SERVICE_URL, "/login")
        
        # 3. 응답 로그
        logger.info(f"✅ Account Service 사용자 로그인 응답: {response.status_code}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Gateway 사용자 로그인 처리 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "사용자 로그인 처리 중 오류가 발생했습니다",
                "error": str(e)
            },
            headers=cors_headers_for(request)
        )

# Account Service 연결 테스트
@app.get("/test-account-service")
async def test_account_service():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ACCOUNT_SERVICE_URL}/health")
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


# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "MSA API Gateway",
        "version": "1.0.0",
        "services": {
            "account": ACCOUNT_SERVICE_URL,
            "chatbot": CHATBOT_SERVICE_URL
        }
    }

# Railway 환경에서 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
