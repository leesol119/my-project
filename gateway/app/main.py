from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import uvicorn
from contextlib import asynccontextmanager

from .router.discovery_router import router as discovery_router
from .router.proxy_router import router as proxy_router
from .router.user_router import router as user_router
from .domain.discovery.controller.proxy_controller import proxy_controller

# Pydantic 모델 정의
class InputData(BaseModel):
    currentInput: str
    timestamp: str
    inputHistory: list[str]
    totalInputs: int

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("Starting Gateway Service...")
    

    
    yield
    
    # 종료 시 실행
    logger.info("Shutting down Gateway Service...")
    await proxy_controller.close()


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="MSA Gateway",
    description="Microservice Architecture Gateway with Service Discovery and Proxy Pattern",
    version="1.0.0",
    lifespan=lifespan
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 프로덕션에서는 특정 호스트로 제한
)


# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if app.debug else "Internal server error"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail
        }
    )


# 라우터 등록
app.include_router(discovery_router)
app.include_router(proxy_router)
app.include_router(user_router)


# 루트 엔드포인트
@app.get("/")
async def root():
    """게이트웨이 루트 엔드포인트"""
    return {
        "message": "MSA Gateway Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "discovery": "/api/discovery",
            "proxy": "/proxy/{service_name}",
            "health": "/api/discovery/health",
            "docs": "/docs"
        }
    }


# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """게이트웨이 헬스 체크"""
    return {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0"
    }


# CORS preflight 요청 처리
@app.options("/api/input")
async def options_input():
    """CORS preflight 요청 처리"""
    return {"message": "OK"}

# 프론트엔드 입력 데이터 수신 엔드포인트
@app.post("/api/input")
async def receive_input_data(input_data: InputData):
    """프론트엔드에서 전송된 입력 데이터를 수신"""
    logger.info("🚗🚗🚗🚗receive_input_data 에 진입 ")
    try:
        # JSON 형태로 전체 데이터 출력 (이미지와 동일한 형태)
        import json
        json_data = {
            "currentInput": input_data.currentInput,
            "timestamp": input_data.timestamp,
            "inputHistory": input_data.inputHistory,
            "totalInputs": input_data.totalInputs
        }
        
        # 보기 좋게 포맷팅된 JSON 출력
        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
        logger.info("=" * 50)
        logger.info("프론트엔드에서 전송된 JSON 데이터:")
        logger.info("=" * 50)
        logger.info(formatted_json)
        logger.info("=" * 50)
        
        # 개별 필드 정보도 함께 출력
        logger.info(f"현재 입력: {input_data.currentInput}")
        logger.info(f"총 입력 횟수: {input_data.totalInputs}")
        logger.info(f"입력 히스토리: {input_data.inputHistory}")
        
        # 여기에 추가 처리 로직을 구현할 수 있습니다
        # 예: 데이터베이스 저장, 다른 서비스로 전달 등
        
        return {
            "status": "success",
            "message": "입력 데이터가 성공적으로 수신되었습니다",
            "received_data": {
                "currentInput": input_data.currentInput,
                "timestamp": input_data.timestamp,
                "totalInputs": input_data.totalInputs,
                "history_length": len(input_data.inputHistory)
            }
        }
    except Exception as e:
        logger.error(f"Error processing input data: {e}")
        raise HTTPException(status_code=500, detail="입력 데이터 처리 중 오류가 발생했습니다")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        
        reload=True,
        log_level="info"
    )
