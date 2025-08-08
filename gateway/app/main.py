
"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 모듈 import
from app.domain.discovery.model.service_discovery import ServiceDiscovery
from app.domain.discovery.model.service_type import ServiceType
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
    # Settings 초기화 및 앱 state에 등록
    try:
        app.state.settings = Settings()
    except:
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

# CORS 미들웨어 설정 - 프로덕션 + 프리뷰 도메인 허용
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://(www\.)?eripotter\.com(/.*)?$",
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
        "*"
    ],
    expose_headers=["*"],
    max_age=86400,
)


# AuthMiddleware가 없는 경우를 위한 임시 처리
try:
    from app.domain.auth.middleware.jwt_auth_middleware import AuthMiddleware
    app.add_middleware(AuthMiddleware)
except ImportError:
    logger.warning("AuthMiddleware not found, skipping authentication middleware")

# 기본 루트 경로
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0", "status": "running"}

# 루트 레벨 헬스 체크
@app.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!"}

# CORS 프리플라이트 요청 처리
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    logger.info(f"🔄 CORS 프리플라이트 요청: {request.method} {path}")
    logger.info(f"📊 Origin: {request.headers.get('origin', 'Unknown')}")
    logger.info(f"📊 User-Agent: {request.headers.get('user-agent', 'Unknown')}")
    
    from fastapi.responses import Response
    import re
    response = Response(status_code=200)
    
    # Origin 헤더 가져오기
    origin = request.headers.get('origin', '')
    
    # 프로덕션 도메인 체크
    production_domains = [
        "https://www.eripotter.com",
        "https://www.eripotter.com/",
    ]
    
    # Vercel 프리뷰 도메인 정규식 패턴
    vercel_preview_pattern = r'^https://.*\.vercel\.app$'
    
    # 도메인 허용 여부 확인
    is_allowed = False
    
    # 1. 프로덕션 도메인 체크
    if origin in production_domains:
        is_allowed = True
        logger.info(f"✅ 프로덕션 도메인 허용: {origin}")
    
    # 2. Vercel 프리뷰 도메인 체크 (정규식)
    elif re.match(vercel_preview_pattern, origin):
        is_allowed = True
        logger.info(f"✅ Vercel 프리뷰 도메인 허용: {origin}")
    
    # 3. 로컬 개발 도메인 체크
    elif origin in ["http://localhost:3000", "http://localhost:3001"]:
        is_allowed = True
        logger.info(f"✅ 로컬 개발 도메인 허용: {origin}")
    
    # CORS 헤더 설정
    if is_allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://www.eripotter.com"
        logger.warning(f"⚠️ 허용되지 않은 도메인: {origin}")
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    
    logger.info(f"✅ CORS 응답 헤더 설정 완료")
    return response

# 로그인 요청 모델
class LoginRequest(BaseModel):
    user_id: str
    user_pw: str

# 회원가입 요청 모델
class SignUpRequest(BaseModel):
    user_id: str
    user_pw: int  # bigint
    company_id: Optional[str] = None  # null 허용

# 전역 변수로 최근 로그인 데이터 저장
latest_login_data = None
# 전역 변수로 최근 회원가입 데이터 저장
latest_signup_data = None

@app.post("/login", summary="로그인")
async def login(request: LoginRequest):
    global latest_login_data
    latest_login_data = request.dict()
    logger.info(f"로그인 요청 받음: {latest_login_data}")
    return {"result": "로그인 성공!", "received_data": latest_login_data}

@app.post("/signup", summary="회원가입")
async def signup(request: SignUpRequest):
    global latest_signup_data
    latest_signup_data = request.dict()
    logger.info(f"🚀 회원가입 요청 받음: {latest_signup_data}")
    logger.info(f"📊 요청 헤더: {request.headers}")
    logger.info(f"🌐 클라이언트 IP: {request.client.host if request.client else 'Unknown'}")
    
    from fastapi.responses import JSONResponse
    import re
    response = JSONResponse(content={"result": "회원가입 성공!", "received_data": latest_signup_data})
    
    # Origin 헤더 가져오기
    origin = request.headers.get('origin', '')
    
    # 프로덕션 도메인 체크
    production_domains = [
        "https://www.eripotter.com",
        "https://www.eripotter.com/",
    ]
    
    # Vercel 프리뷰 도메인 정규식 패턴
    vercel_preview_pattern = r'^https://.*\.vercel\.app$'
    
    # 도메인 허용 여부 확인
    is_allowed = False
    
    # 1. 프로덕션 도메인 체크
    if origin in production_domains:
        is_allowed = True
        logger.info(f"✅ 프로덕션 도메인 허용: {origin}")
    
    # 2. Vercel 프리뷰 도메인 체크 (정규식)
    elif re.match(vercel_preview_pattern, origin):
        is_allowed = True
        logger.info(f"✅ Vercel 프리뷰 도메인 허용: {origin}")
    
    # 3. 로컬 개발 도메인 체크
    elif origin in ["http://localhost:3000", "http://localhost:3001"]:
        is_allowed = True
        logger.info(f"✅ 로컬 개발 도메인 허용: {origin}")
    
    # CORS 헤더 설정
    if is_allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://www.eripotter.com"
        logger.warning(f"⚠️ 허용되지 않은 도메인: {origin}")
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
    
    return response

@app.get("/login", summary="최근 로그인 데이터 확인")
async def get_latest_login():
    global latest_login_data
    if latest_login_data:
        return latest_login_data
    else:
        return {
            "message": "아직 로그인 데이터가 없습니다",
            "description": "프론트엔드에서 로그인 버튼을 클릭하면 데이터가 표시됩니다"
        }

@app.get("/signup", summary="최근 회원가입 데이터 확인")
async def get_latest_signup():
    global latest_signup_data
    if latest_signup_data:
        return latest_signup_data
    else:
        return {
            "message": "아직 회원가입 데이터가 없습니다",
            "description": "프론트엔드에서 회원가입 버튼을 클릭하면 데이터가 표시됩니다"
        }

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])

# 라우터 등록 (현재 존재하는 라우터만)
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

# 🪡🪡🪡 파일이 필요한 서비스 목록 (현재는 없음)
FILE_REQUIRED_SERVICES = set()

@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: str, 
    path: str, 
    request: Request
):
    try:
        factory = ServiceDiscovery(service_type=service)
        
        # 헤더 전달
        headers = dict(request.headers)
        
        response = await factory.request(
            method="GET",
            path=path,
            headers=headers
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in GET proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 파일 업로드 및 일반 JSON 요청 모두 처리
@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: str, 
    path: str,
    request: Request,
    file: Optional[UploadFile] = None,
    sheet_names: Optional[List[str]] = Query(None, alias="sheet_name")
):
    try:
        # 로깅
        logger.info(f"🌈 POST 요청 받음: 서비스={service}, 경로={path}")
        if file:
            logger.info(f"파일명: {file.filename}, 시트 이름: {sheet_names if sheet_names else '없음'}")

        # 서비스 팩토리 생성
        factory = ServiceDiscovery(service_type=service)
        
        # 요청 파라미터 초기화
        files = None
        params = None
        body = None
        data = None
        
        # 헤더 전달
        headers = dict(request.headers)
        
        # 파일이 필요한 서비스 처리
        if service in FILE_REQUIRED_SERVICES:
            # 파일이 필요한 서비스인 경우
            
            # 서비스 URI가 upload인 경우만 파일 체크
            if "upload" in path and not file:
                raise HTTPException(status_code=400, detail=f"서비스 {service}에는 파일 업로드가 필요합니다.")
            
            # 파일이 제공된 경우 처리
            if file:
                file_content = await file.read()
                files = {'file': (file.filename, file_content, file.content_type)}
                
                # 파일 위치 되돌리기 (다른 코드에서 다시 읽을 수 있도록)
                await file.seek(0)
            
            # 시트 이름이 제공된 경우 처리
            if sheet_names:
                params = {'sheet_name': sheet_names}
        else:
            # 일반 서비스 처리 (body JSON 전달)
            try:
                body = await request.body()
                if not body:
                    # body가 비어있는 경우도 허용
                    logger.info("요청 본문이 비어 있습니다.")
            except Exception as e:
                logger.warning(f"요청 본문 읽기 실패: {str(e)}")
                
        # 서비스에 요청 전달
        response = await factory.request(
            method="POST",
            path=path,
            headers=headers,
            body=body,
            files=files,
            params=params,
            data=data
        )
        
        # 응답 처리 및 반환
        return ResponseFactory.create_response(response)
        
    except HTTPException as he:
        # HTTP 예외는 그대로 반환
        return JSONResponse(
            content={"detail": he.detail},
            status_code=he.status_code
        )
    except Exception as e:
        # 일반 예외는 로깅 후 500 에러 반환
        logger.error(f"POST 요청 처리 중 오류 발생: {str(e)}")
        return JSONResponse(
            content={"detail": f"Gateway error: {str(e)}"},
            status_code=500
        )

# PUT - 일반 동적 라우팅
@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        
        # 헤더 전달
        headers = dict(request.headers)
        
        response = await factory.request(
            method="PUT",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PUT proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# DELETE - 일반 동적 라우팅
@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        
        # 헤더 전달
        headers = dict(request.headers)
        
        response = await factory.request(
            method="DELETE",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in DELETE proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# PATCH - 일반 동적 라우팅
@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    try:
        factory = ServiceDiscovery(service_type=service)
        
        # 헤더 전달
        headers = dict(request.headers)
        
        response = await factory.request(
            method="PATCH",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PATCH proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 404 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "요청한 리소스를 찾을 수 없습니다."}
    )

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)