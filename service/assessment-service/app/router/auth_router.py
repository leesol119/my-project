"""
Assessment Service Auth Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AuthRequest(BaseModel):
    user_id: str
    password: str

class AuthResponse(BaseModel):
    user_id: str
    token: str
    status: str

@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    """사용자 로그인"""
    try:
        # 실제 구현에서는 데이터베이스에서 사용자 확인
        token = f"token_{request.user_id}_{request.password}"
        
        response = AuthResponse(
            user_id=request.user_id,
            token=token,
            status="authenticated"
        )
        
        logger.info(f"User logged in: {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.get("/verify")
async def verify_token():
    """토큰 검증"""
    return {"status": "valid", "message": "Token is valid"}
