from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from typing import Dict, Any
from ..domain.discovery.controller.proxy_controller import proxy_controller

router = APIRouter(prefix="/proxy", tags=["Proxy"])


@router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_to_service(request: Request, service_name: str, path: str = ""):
    """모든 HTTP 메서드를 대상 서비스로 프록시"""
    return await proxy_controller.proxy_request(request, service_name, path)


@router.api_route("/{service_name}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_to_service_root(request: Request, service_name: str):
    """루트 경로로 프록시"""
    return await proxy_controller.proxy_request(request, service_name, "") 