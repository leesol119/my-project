@echo off

REM Assessment Service Railway 배포 스크립트 (Windows)

echo 🚀 Assessment Service Railway 배포 시작...

REM Railway CLI 설치 확인
railway --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI가 설치되지 않았습니다.
    echo 다음 명령어로 설치하세요: npm install -g @railway/cli
    pause
    exit /b 1
)

REM Railway 로그인 확인
railway whoami >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway에 로그인되지 않았습니다.
    echo 다음 명령어로 로그인하세요: railway login
    pause
    exit /b 1
)

REM 현재 디렉토리 확인
echo 📁 현재 디렉토리: %CD%
echo 📁 파일 목록:
dir

REM Dockerfile 존재 확인
if exist "Dockerfile" (
    echo ✅ Dockerfile 발견
) else (
    echo ❌ Dockerfile이 없습니다. NIXPACKS 빌더를 사용합니다.
)

REM 프로젝트 초기화 (이미 초기화된 경우 스킵)
if not exist ".railway" (
    echo 📦 Railway 프로젝트 초기화...
    railway init
)

REM 환경 변수 설정 확인
echo 🔧 환경 변수 설정 확인...
if "%RAILWAY_ENVIRONMENT%"=="" (
    echo ⚠️  RAILWAY_ENVIRONMENT 환경 변수가 설정되지 않았습니다.
    echo Railway 대시보드에서 환경 변수를 설정하세요.
)

REM 배포 실행
echo 🚀 배포 시작...
railway up

echo ✅ 배포 완료!
echo 📋 배포된 서비스 URL을 확인하려면: railway status
pause
