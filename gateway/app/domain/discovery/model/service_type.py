"""
Service Type 정의
"""
from enum import Enum

class ServiceType(Enum):
    ASSESSMENT = "assessment"
    CHATBOT = "chatbot"
    MONITORING = "monitoring"
    REPORT = "report"
    REQUEST = "request"
    RESPONSE = "response"
