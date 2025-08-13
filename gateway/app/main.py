"""
Gateway API 메인 파일 - 서비스 디스커버리 역할
CORS 문제 근본 해결 버전
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
import httpx
import logging
import os
import re
from contextlib import asynccontextmanager

# ---------------------------
# 로깅 설정
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

# ---------------------------
# 서비스 URL 설정
# ---------------------------
ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8003")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")

# Railway 환경에서는 서비스 URL을 환경변수에서 가져옴
if os.getenv("RAILWAY_ENVIRONMENT") == "true":
    # 실제 Account/Chatbot Service URL 환경변수로 주입되어야 함
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", ACCOUNT_SERVICE_URL)
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", CHATBOT_SERVICE_URL)
    logger.info("🚀 Railway 환경 감지")

# 로컬 개발 환경에서는 Docker Compose 네트워크 사용
if os.getenv("ENVIRONMENT") == "development":
    ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8003")
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8004")
    logger.info("🔧 개발 환경 감지")

logger.info(f"📡 Account Service URL: {ACCOUNT_SERVICE_URL}")
logger.info(f"📡 Chatbot  Service URL: {CHATBOT_SERVICE_URL}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    logger.info(f"📡 Account Service URL: {ACCOUNT_SERVICE_URL}")
    logger.info(f"📡 Chatbot  Service URL: {CHATBOT_SERVICE_URL}")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for EriPotter Project - Service Discovery",
    version="0.1.0",
    lifespan=lifespan
)

# ---------------------------
# CORS 미들웨어 설정
# ---------------------------
# eripotter.com(서브도메인 포함) / localhost:3000,3001 / 192.168.*.*:3000,3001 허용
ALLOW_ORIGIN_REGEX = r"^https:\/\/([a-z0-9-]+\.)*eripotter\.com$|^https?:\/\/localhost:(3000|3001)$|^https?:\/\/192\.168\.\d+\.\d+:(3000|3001)$"
_allow_origin_re = re.compile(ALLOW_ORIGIN_REGEX)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=False,  # 쿠키/세션 필요 시 True로 변경 (이 경우 Origin 와일드카드 금지)
    max_age=86400,
)

def _origin_allowed(origin: str | None) -> bool:
    if not origin:
        return False
    return bool(_allow_origin_re.match(origin))

# ---------------------------
# HTTP 클라이언트
# ---------------------------
http_client = httpx.AsyncClient(timeout=30.0)

# ---------------------------
# 범용 프록시 함수
# ---------------------------
async def _proxy(request: Request, service_url: str, path: str):
    """서비스로 요청을 프록시하는 범용 함수"""
    method = request.method
    target_url = f"{service_url}/{path.lstrip('/')}"
    origin = request.headers.get("origin")

    logger.info(f"PROXY {method} {target_url} origin={origin}")
    logger.info(f"Service URL: {service_url}")

    try:
        # 요청 본문 읽기
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                logger.info(f"Request body: {body}")
            except Exception as e:
                logger.warning(f"JSON 파싱 실패, 바이너리로 처리: {e}")
                body = await request.body()

        # 헤더 준비 (hop-by-hop 헤더 제거)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        logger.info(f"Request headers: {headers}")

        # 서비스로 요청 전송
        logger.info(f"서비스로 요청 전송 중: {target_url}")
        response = await http_client.request(
            method=method,
            url=target_url,
            json=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None,
            headers=headers,
            params=request.query_params
        )

        logger.info(f"Service 응답: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")

        # 응답 생성
        # JSON이면 JSON으로, 아니면 텍스트로
        content_type = response.headers.get("content-type", "")
        content = (
            response.json()
            if content_type.startswith("application/json")
            else response.text
        )

        # 다운스트림 헤더를 그대로 복사하되, hop-by-hop/민감 헤더는 제거
        passthrough_headers = dict(response.headers)
        for h in ["content-length", "transfer-encoding", "connection", "keep-alive", "proxy-authenticate",
                  "proxy-authorization", "te", "trailers", "upgrade"]:
            passthrough_headers.pop(h, None)

        return JSONResponse(
            status_code=response.status_code,
            content=content,
            headers=passthrough_headers
        )

    except httpx.RequestError as e:
        logger.error(f"Service 연결 오류: {e}")
        logger.error(f"Service URL: {service_url}")
        logger.error(f"Target URL: {target_url}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(status_code=503, detail=f"Service 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"프록시 오류: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail="프록시 오류")

# ---------------------------
# 기본 엔드포인트
# ---------------------------
@app.get("/")
async def root():
    return {"message": "Gateway API - Service Discovery", "version": "0.1.0", "status": "running"}

@app.get("/favicon.ico")
async def favicon():
    """favicon.ico 요청 처리 - 502 오류 방지"""
    logger.info("FAVICON 요청")
    return JSONResponse(status_code=204, content=None)

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

# ---------------------------
# CORS 프리플라이트 핸들러 (모든 경로)
# ---------------------------
@app.options("/{path:path}")
async def preflight_handler(path: str, request: Request):
    origin = request.headers.get("origin")
    req_headers = request.headers.get("access-control-request-headers", "*")
    methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS"

    logger.info(f"PREFLIGHT {path} origin={origin} req_headers={req_headers}")

    # 허용되지 않은 Origin이면 403 (선택 사항: 필요 시 완화 가능)
    if not _origin_allowed(origin):
        logger.warning(f"❌ 비허용 Origin의 프리플라이트: {origin}")
        return PlainTextResponse("Forbidden origin", status_code=403)

    headers = {
        "Access-Control-Allow-Origin": origin,         # echo allowed origin
        "Access-Control-Allow-Methods": methods,
        "Access-Control-Allow-Headers": req_headers,
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin",  # 캐시 분리
    }
    return Response(status_code=200, headers=headers)

# ---------------------------
# 프록시 라우트
# ---------------------------
# ---- account-service 프록시 ----
@app.api_route("/api/account", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def account_root(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/")

@app.api_route("/api/account/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def account_any(path: str, request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, path)

# ---- chatbot-service 프록시 ----
@app.api_route("/api/chatbot", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def chatbot_root(request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, "/")

@app.api_route("/api/chatbot/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def chatbot_any(path: str, request: Request):
    return await _proxy(request, CHATBOT_SERVICE_URL, path)

# ---- 기존 경로 호환성 유지 (점진적 마이그레이션용) ----
@app.post("/login")
async def login_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/login")

@app.post("/signup")
async def signup_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/signup")

@app.post("/user/login")
async def user_login_proxy(request: Request):
    return await _proxy(request, ACCOUNT_SERVICE_URL, "/login")

# ---------------------------
# 서버 실행
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    # 고정 포트 사용 (Railway는 PORT 환경변수를 세팅해줄 수 있으니 필요하면 교체)
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
