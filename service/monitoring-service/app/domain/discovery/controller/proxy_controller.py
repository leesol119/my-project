from typing import Optional, Dict, Any
import httpx
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import json
import logging
from ..model.service_registry import service_registry, ServiceInfo

logger = logging.getLogger(__name__)


class ProxyController:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def proxy_request(self, request: Request, service_name: str, path: str = "") -> Response:
        """요청을 대상 서비스로 프록시"""
        try:
            # 서비스 정보 조회
            service = service_registry.get_service(service_name)
            if not service:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
            
            if service.status.value != "healthy":
                raise HTTPException(status_code=503, detail=f"Service '{service_name}' is unhealthy")
            
            # 대상 URL 구성
            target_url = f"{service.base_url.rstrip('/')}/{path.lstrip('/')}"
            
            # 요청 헤더 복사 (호스트 헤더 제외)
            headers = dict(request.headers)
            headers.pop("host", None)
            
            # 요청 바디 읽기
            body = await request.body()
            
            # 프록시 요청 수행
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # 응답 헤더 구성
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)  # 압축 해제를 위해 제거
            
            # 스트리밍 응답 반환
            return StreamingResponse(
                content=self._stream_response(response),
                status_code=response.status_code,
                headers=response_headers
            )
            
        except httpx.RequestError as e:
            logger.error(f"Proxy request failed for {service_name}: {e}")
            raise HTTPException(status_code=502, detail="Bad Gateway")
        except Exception as e:
            logger.error(f"Unexpected error in proxy: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    async def _stream_response(self, response: httpx.Response):
        """응답을 스트리밍으로 전송"""
        async for chunk in response.aiter_bytes():
            yield chunk
    
    async def register_service(self, service_info: ServiceInfo) -> Dict[str, Any]:
        """서비스 등록"""
        try:
            success = await service_registry.register_service(service_info)
            if success:
                return {
                    "success": True,
                    "message": f"Service '{service_info.service_name}' registered successfully",
                    "service": service_info.dict()
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to register service")
        except Exception as e:
            logger.error(f"Service registration failed: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    async def unregister_service(self, service_name: str) -> Dict[str, Any]:
        """서비스 등록 해제"""
        try:
            success = await service_registry.unregister_service(service_name)
            if success:
                return {
                    "success": True,
                    "message": f"Service '{service_name}' unregistered successfully"
                }
            else:
                raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        except Exception as e:
            logger.error(f"Service unregistration failed: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """서비스 상태 조회"""
        service = service_registry.get_service(service_name)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        
        return {
            "service_name": service.service_name,
            "base_url": service.base_url,
            "status": service.status.value,
            "last_health_check": service.last_health_check.isoformat() if service.last_health_check else None,
            "response_time": service.response_time,
            "metadata": service.metadata
        }
    
    def get_all_services(self) -> Dict[str, Any]:
        """모든 서비스 상태 조회"""
        services = service_registry.get_all_services()
        return {
            "services": [
                {
                    "service_name": service.service_name,
                    "base_url": service.base_url,
                    "status": service.status.value,
                    "last_health_check": service.last_health_check.isoformat() if service.last_health_check else None,
                    "response_time": service.response_time,
                    "metadata": service.metadata
                }
                for service in services
            ],
            "total_count": len(services),
            "healthy_count": len(service_registry.get_healthy_services())
        }
    
    async def close(self):
        """리소스 정리"""
        await self.client.aclose()


# 전역 프록시 컨트롤러 인스턴스
proxy_controller = ProxyController() 