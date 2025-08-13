
from fastapi import APIRouter, Cookie, HTTPException, Query
from fastapi.responses import JSONResponse

# from app.domain.auth.controller.google_controller import GoogleController

auth_router = APIRouter(prefix="/auth", tags=["auth"])
# google_controller = GoogleController()

@auth_router.get("/google/login", summary="Google 로그인 시작")
async def google_login(
    redirect_uri: str = Query(
        default="http://localhost:3000/dashboard",
        description="로그인 후 리다이렉트할 URI (기본값: /dashboard)"
    )
):
    """
    Google OAuth 로그인을 시작합니다.
    """
    return {"message": "Google 로그인 기능 준비 중"}

@auth_router.get("/google/callback", summary="Google OAuth 콜백 처리")
async def google_callback(
    code: str = Query(..., description="Google OAuth 인증 코드"),
    state: str = Query(..., description="로그인 시작 시 전달한 state 값")
):
    """
    Google OAuth 콜백을 처리합니다.
    """
    return {"message": "Google 콜백 기능 준비 중"}

@auth_router.post("/logout", summary="로그아웃")
async def logout(session_token: str | None = Cookie(None)):
    """
    사용자를 로그아웃하고 인증 쿠키를 삭제합니다.
    """
    print(f"로그아웃 요청 - 받은 세션 토큰: {session_token}")
    
    # 로그아웃 응답 생성
    response = JSONResponse({
        "success": True,
        "message": "로그아웃되었습니다."
    })
    
    # 인증 쿠키 삭제
    response.delete_cookie(
        key="session_token",
        path="/",
    )
    
    print("✅ 로그아웃 완료 - 인증 쿠키 삭제됨")
    return response

@auth_router.get("/profile", summary="사용자 프로필 조회")
async def get_profile(session_token: str | None = Cookie(None)):
    """
    세션 토큰으로 사용자 프로필을 조회합니다.
    """
    print(f"프로필 요청 - 받은 세션 토큰: {session_token}")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="인증 쿠키가 없습니다.")
    
    return {"message": "프로필 조회 기능 준비 중"}