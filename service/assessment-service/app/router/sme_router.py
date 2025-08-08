"""
Assessment Service SME (Small and Medium Enterprise) Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SMERequest(BaseModel):
    company_id: str
    assessment_type: str
    data: dict

class SMEResponse(BaseModel):
    company_id: str
    assessment_type: str
    score: float
    recommendations: List[str]

@router.post("/assessment", response_model=SMEResponse)
async def create_sme_assessment(request: SMERequest):
    """중소기업 평가 생성"""
    try:
        response = SMEResponse(
            company_id=request.company_id,
            assessment_type=request.assessment_type,
            score=78.5,
            recommendations=[
                "생산성 향상을 위한 자동화 도입",
                "공급망 최적화 방안 수립",
                "품질 관리 시스템 구축"
            ]
        )
        
        logger.info(f"SME assessment created: {request.company_id}")
        return response
        
    except Exception as e:
        logger.error(f"SME assessment creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Assessment creation failed")

@router.get("/companies")
async def get_sme_companies():
    """중소기업 목록 조회"""
    return {
        "companies": [
            {"id": "sme_001", "name": "중소기업 A", "type": "manufacturing"},
            {"id": "sme_002", "name": "중소기업 B", "type": "service"}
        ]
    }
