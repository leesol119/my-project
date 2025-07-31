from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/")
async def get_users():
    """사용자 목록 조회 (프록시를 통해 user-service로 전달)"""
    return {
        "message": "This endpoint should be proxied to user-service",
        "endpoint": "/proxy/user-service/api/users"
    }


@router.get("/{user_id}")
async def get_user(user_id: str):
    """특정 사용자 조회 (프록시를 통해 user-service로 전달)"""
    return {
        "message": "This endpoint should be proxied to user-service",
        "endpoint": f"/proxy/user-service/api/users/{user_id}"
    }


@router.post("/")
async def create_user():
    """사용자 생성 (프록시를 통해 user-service로 전달)"""
    return {
        "message": "This endpoint should be proxied to user-service",
        "endpoint": "/proxy/user-service/api/users"
    }


@router.put("/{user_id}")
async def update_user(user_id: str):
    """사용자 정보 수정 (프록시를 통해 user-service로 전달)"""
    return {
        "message": "This endpoint should be proxied to user-service",
        "endpoint": f"/proxy/user-service/api/users/{user_id}"
    }


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """사용자 삭제 (프록시를 통해 user-service로 전달)"""
    return {
        "message": "This endpoint should be proxied to user-service",
        "endpoint": f"/proxy/user-service/api/users/{user_id}"
    }
