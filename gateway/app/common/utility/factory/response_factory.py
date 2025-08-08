"""
응답 팩토리
"""
from typing import Any, Dict
from fastapi.responses import JSONResponse

class ResponseFactory:
    @staticmethod
    def create_response(response_data: Any) -> JSONResponse:
        """응답 데이터를 JSONResponse로 변환"""
        if isinstance(response_data, dict):
            return JSONResponse(content=response_data)
        else:
            return JSONResponse(content={"data": response_data})
