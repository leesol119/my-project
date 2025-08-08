from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
import httpx
from enum import Enum


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceInfo(BaseModel):
    service_name: str
    base_url: str
    health_check_url: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time: Optional[float] = None
    metadata: Dict[str, str] = {}


class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def register_service(self, service_info: ServiceInfo) -> bool:
        """서비스를 레지스트리에 등록"""
        self._services[service_info.service_name] = service_info
        await self._start_health_check()
        return True
    
    async def unregister_service(self, service_name: str) -> bool:
        """서비스를 레지스트리에서 제거"""
        if service_name in self._services:
            del self._services[service_name]
            return True
        return False
    
    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """서비스 정보 조회"""
        return self._services.get(service_name)
    
    def get_all_services(self) -> List[ServiceInfo]:
        """모든 서비스 정보 조회"""
        return list(self._services.values())
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """건강한 서비스만 조회"""
        return [service for service in self._services.values() 
                if service.status == ServiceStatus.HEALTHY]
    
    async def _start_health_check(self):
        """헬스 체크 태스크 시작"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """주기적으로 서비스 헬스 체크 수행"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._health_check_interval)
            except Exception as e:
                print(f"Health check error: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """모든 서비스에 대해 헬스 체크 수행"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = []
            for service in self._services.values():
                task = asyncio.create_task(self._check_service_health(client, service))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, client: httpx.AsyncClient, service: ServiceInfo):
        """개별 서비스 헬스 체크"""
        try:
            start_time = datetime.now()
            response = await client.get(service.health_check_url)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                service.status = ServiceStatus.HEALTHY
            else:
                service.status = ServiceStatus.UNHEALTHY
            
            service.last_health_check = datetime.now()
            service.response_time = response_time
            
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            service.last_health_check = datetime.now()
            print(f"Health check failed for {service.service_name}: {e}")


# 전역 서비스 레지스트리 인스턴스
service_registry = ServiceRegistry() 