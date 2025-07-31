#!/usr/bin/env python3
"""
MSA Gateway 설치 테스트 스크립트
"""

def test_imports():
    """필수 패키지들이 정상적으로 import되는지 테스트"""
    try:
        print("Testing imports...")
        
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
        
        import uvicorn
        print(f"✓ Uvicorn {uvicorn.__version__}")
        
        import httpx
        print(f"✓ HTTPX {httpx.__version__}")
        
        import pydantic
        print(f"✓ Pydantic {pydantic.__version__}")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_app_creation():
    """FastAPI 앱 생성 테스트"""
    try:
        print("\nTesting FastAPI app creation...")
        
        from fastapi import FastAPI
        app = FastAPI(title="Test App")
        
        print("✓ FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False

def test_proxy_components():
    """프록시 관련 컴포넌트 테스트"""
    try:
        print("\nTesting proxy components...")
        
        # 서비스 레지스트리 테스트
        from app.domain.discovery.model.service_registry import ServiceInfo, ServiceStatus
        service = ServiceInfo(
            service_name="test-service",
            base_url="http://localhost:8080",
            health_check_url="http://localhost:8080/health"
        )
        print("✓ Service registry components working")
        
        return True
        
    except Exception as e:
        print(f"✗ Proxy components test failed: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("MSA Gateway Installation Test")
    print("=" * 40)
    
    success = True
    
    # Import 테스트
    if not test_imports():
        success = False
    
    # 앱 생성 테스트
    if not test_app_creation():
        success = False
    
    # 프록시 컴포넌트 테스트
    if not test_proxy_components():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Installation is successful.")
        print("\nTo run the gateway:")
        print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\nOr using Docker:")
        print("docker-compose up --build")
    else:
        print("✗ Some tests failed. Please check the installation.")
        print("\nTry running the installation script again:")
        print("Windows: install.bat")
        print("Linux/Mac: ./install.sh")

if __name__ == "__main__":
    main() 