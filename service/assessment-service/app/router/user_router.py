"""
Assessment Service User Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class UserRequest(BaseModel):
    user_id: str
    email: str
    company_type: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    company_type: str
    status: str

@router.post("/register", response_model=UserResponse)
async def register_user(request: UserRequest):
    """사용자 등록"""
    try:
        response = UserResponse(
            user_id=request.user_id,
            email=request.email,
            company_type=request.company_type or "unknown",
            status="registered"
        )
        
        logger.info(f"User registered: {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.get("/{user_id}")
async def get_user(user_id: str):
    """사용자 정보 조회"""
    try:
        return {
            "user_id": user_id,
            "email": f"{user_id}@example.com",
            "company_type": "LME",
            "status": "active"
        }
    except Exception as e:
        logger.error(f"User retrieval failed: {str(e)}")
        raise HTTPException(status_code=404, detail="User not found")
