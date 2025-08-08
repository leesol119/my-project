"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import os
import logging
import sys
import re
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 모듈 import
from app.domain.discovery.model.service_discovery import ServiceDiscovery
from app.common.utility.constant.settings import Settings
from app.common.utility.factory.response_factory import ResponseFactory

if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    try:
        app.state.settings = Settings()
    except Exception:
        app.state.settings = None
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for EriPotter Project",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

# ──────────────────────────────────────────────────────────────────────────────
# 0) CORS 미들웨어: 도메인만 매칭 (경로 불포함)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://(www\.)?eripotter\.com$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "*",
    ],
    expose_headers=["*"],
    max_age=86400,
)

# 1) OPTIONS는 어떤 미들웨어/인증보다 먼저 무조건 통과시키기
@app.middleware("http")
async def allow_cors_preflight(request: Request, call_next):
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "")
        resp = Response(status_code=200)
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        resp.headers["Access-Control-Allow-Headers"] = (
            "Accept, Accept-Language, Content-Language, Content-Type, Authorization, "
            "X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        )
        resp.headers["Access-Control-Max-Age"] = "86400"
        return resp
    return await call_next(request)

# 2) (선택) Auth 미들웨어: OPTIONS는 위에서 이미 빠지므로 안전
try:
    from app.domain.auth.middleware.jwt_auth_middleware import AuthMiddleware
    app.add_middleware(AuthMiddleware)
except ImportError:
    logger.warning("AuthMiddleware not found, skipping authentication middleware")

# ──────────────────────────────────────────────────────────────────────────────
# 기본 루트 경로 & 헬스 체크
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0", "status": "running"}

@app.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!"}

# 3) 범용 OPTIONS 핸들러 (로그 + 안전망)
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    logger.info(f"🔄 CORS 프리플라이트 요청: {request.method} {path}")
    origin = request.headers.get("origin", "")
    response = Response(status_code=200)
    # 허용 도메인 판정 (프로덕션/프리뷰/로컬)
    production_domains = ["https://www.eripotter.com", "https://www.eripotter.com/"]
    vercel_preview_pattern = r"^https://.*\.vercel\.app$"

    is_allowed = (
        origin in production_domains
        or re.match(vercel_preview_pattern, origin) is not None
        or origin in ["http://localhost:3000", "http://localhost:3001"]
    )
    response.headers["Access-Control-Allow-Origin"] = origin if is_allowed else "https://www.eripotter.com"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = (
        "Accept, Accept-Language, Content-Language, Content-Type, Authorization, "
        "X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
    )
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# ──────────────────────────────────────────────────────────────────────────────
# 요청 모델
class LoginRequest(BaseModel):
    user_id: str
    user_pw: str

class SignUpRequest(BaseModel):
    user_id: str
    user_pw: int          # bigint
    company_id: Optional[str] = None  # null 허용

# 최근 데이터 저장 (디버깅용)
latest_login_data = None
latest_signup_data = None

@app.post("/login", summary="로그인")
async def login(req: LoginRequest):
    global latest_login_data
    latest_login_data = req.dict()
    logger.info(f"로그인 요청 받음: {latest_login_data}")
    return {"result": "로그인 성공!", "received_data": latest_login_data}

# 4) /signup 전용 OPTIONS (안전망 2)
@app.options("/signup")
async def signup_options_handler(request: Request):
    logger.info("🔄 /signup CORS 프리플라이트 요청")
    origin = request.headers.get("origin", "")
    resp = JSONResponse(status_code=200, content={})
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    resp.headers["Access-Control-Allow-Headers"] = (
        "Accept, Accept-Language, Content-Language, Content-Type, Authorization, "
        "X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
    )
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp

@app.post("/signup", summary="회원가입")
async def signup(request_data: SignUpRequest, request: Request):
    global latest_signup_data
    latest_signup_data = request_data.dict()
    logger.info(f"🚀 회원가입 요청 받음: {latest_signup_data}")
    logger.info(f"📊 요청 헤더: {dict(request.headers)}")
    logger.info(f"🌐 클라이언트 IP: {request.client.host if request.client else 'Unknown'}")

    resp = JSONResponse(content={"result": "회원가입 성공!", "received_data": latest_signup_data})

    origin = request.headers.get("origin", "")
    production_domains = ["https://www.eripotter.com", "https://www.eripotter.com/"]
    vercel_preview_pattern = r"^https://.*\.vercel\.app$"

    is_allowed = (
        origin in production_domains
        or re.match(vercel_preview_pattern, origin) is not None
        or origin in ["http://localhost:3000", "http://localhost:3001"]
    )
    resp.headers["Access-Control-Allow-Origin"] = origin if is_allowed else "https://www.eripotter.com"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    resp.headers["Access-Control-Allow-Headers"] = (
        "Accept, Accept-Language, Content-Language, Content-Type, Authorization, "
        "X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
    )
    return resp

@app.get("/login", summary="최근 로그인 데이터 확인")
async def get_latest_login():
    return latest_login_data or {
        "message": "아직 로그인 데이터가 없습니다",
        "description": "프론트엔드에서 로그인 버튼을 클릭하면 데이터가 표시됩니다",
    }

@app.get("/signup", summary="최근 회원가입 데이터 확인")
async def get_latest_signup():
    return latest_signup_data or {
        "message": "아직 회원가입 데이터가 없습니다",
        "description": "프론트엔드에서 회원가입 버튼을 클릭하면 데이터가 표시됩니다",
    }

# ──────────────────────────────────────────────────────────────────────────────
# 프록시 라우터
gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])

try:
    from app.router.assesment_router import assesment_router
    gateway_router.include_router(assesment_router)
except ImportError:
    logger.warning("assesment_router not found")

try:
    from app.router.chatbot_router import chatbot_router
    gateway_router.include_router(chatbot_router)
except ImportError:
    logger.warning("chatbot_router not found")

try:
    from app.router.monitoring_router import monitoring_router
    gateway_router.include_router(monitoring_router)
except ImportError:
    logger.warning("monitoring_router not found")

app.include_router(gateway_router)

# 파일이 필요한 서비스 목록 (현재는 없음)
FILE_REQUIRED_SERVICES = set()

@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        headers = dict(request.headers)
        response = await factory.request(method="GET", path=path, headers=headers)
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in GET proxy: {str(e)}")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: str,
    path: str,
    request: Request,
    file: Optional[UploadFile] = None,
    sheet_names: Optional[List[str]] = Query(None, alias="sheet_name"),
):
    try:
        logger.info(f"🌈 POST 요청 받음: 서비스={service}, 경로={path}")
        if file:
            logger.info(f"파일명: {file.filename}, 시트 이름: {sheet_names if sheet_names else '없음'}")

        factory = ServiceDiscovery(service_type=service)
        files = None
        params = None
        body = None
        data = None
        headers = dict(request.headers)

        if service in FILE_REQUIRED_SERVICES:
            if "upload" in path and not file:
                raise HTTPException(status_code=400, detail=f"서비스 {service}에는 파일 업로드가 필요합니다.")
            if file:
                file_content = await file.read()
                files = {"file": (file.filename, file_content, file.content_type)}
                await file.seek(0)
            if sheet_names:
                params = {"sheet_name": sheet_names}
        else:
            try:
                body = await request.body()
                if not body:
                    logger.info("요청 본문이 비어 있습니다.")
            except Exception as e:
                logger.warning(f"요청 본문 읽기 실패: {str(e)}")

        response = await factory.request(
            method="POST", path=path, headers=headers, body=body, files=files, params=params, data=data
        )
        return ResponseFactory.create_response(response)

    except HTTPException as he:
        return JSONResponse(content={"detail": he.detail}, status_code=he.status_code)
    except Exception as e:
        logger.error(f"POST 요청 처리 중 오류 발생: {str(e)}")
        return JSONResponse(content={"detail": f"Gateway error: {str(e)}"}, status_code=500)

@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        headers = dict(request.headers)
        response = await factory.request(method="PUT", path=path, headers=headers, body=await request.body())
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PUT proxy: {str(e)}")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        headers = dict(request.headers)
        response = await factory.request(method="DELETE", path=path, headers=headers, body=await request.body())
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in DELETE proxy: {str(e)}")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        headers = dict(request.headers)
        response = await factory.request(method="PATCH", path=path, headers=headers, body=await request.body())
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PATCH proxy: {str(e)}")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

# 404 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "요청한 리소스를 찾을 수 없습니다."})

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
