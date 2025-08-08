"""
설정 상수
"""
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.railway_environment = os.getenv("RAILWAY_ENVIRONMENT", "false")
        self.service_port = int(os.getenv("SERVICE_PORT", 8080))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
    @property
    def is_railway(self) -> bool:
        return self.railway_environment == "true"
