from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..domain.discovery.controller.proxy_controller import proxy_controller
from ..domain.discovery.model.service_registry import ServiceInfo

router = APIRouter(prefix="/api/discovery", tags=["Service Discovery"])


@router.post("/services")
async def register_service(service_info: ServiceInfo):
    """서비스 등록"""
    return await proxy_controller.register_service(service_info)


@router.delete("/services/{service_name}")
async def unregister_service(service_name: str):
    """서비스 등록 해제"""
    return await proxy_controller.unregister_service(service_name)


@router.get("/services")
async def get_all_services():
    """모든 서비스 상태 조회"""
    return proxy_controller.get_all_services()


@router.get("/services/{service_name}")
async def get_service_status(service_name: str):
    """특정 서비스 상태 조회"""
    return proxy_controller.get_service_status(service_name)


@router.get("/health")
async def health_check():
    """게이트웨이 헬스 체크"""
    return {
        "status": "healthy",
        "service": "gateway",
        "message": "Gateway is running"
    } 