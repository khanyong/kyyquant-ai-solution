"""
n8n 서버 연동 설정
NAS에 설치된 n8n 서버와 통신하기 위한 설정
"""

import os
from dotenv import load_dotenv

load_dotenv()

class N8NConfig:
    """n8n 서버 설정"""
    
    # NAS n8n 서버 정보
    N8N_HOST = os.getenv('N8N_HOST', 'your-nas-ip')  # NAS IP 주소
    N8N_PORT = os.getenv('N8N_PORT', '5678')
    N8N_PROTOCOL = os.getenv('N8N_PROTOCOL', 'http')
    
    # n8n API 인증 정보
    N8N_API_KEY = os.getenv('N8N_API_KEY', '')
    N8N_BASIC_AUTH_USER = os.getenv('N8N_BASIC_AUTH_USER', '')
    N8N_BASIC_AUTH_PASSWORD = os.getenv('N8N_BASIC_AUTH_PASSWORD', '')
    
    # Webhook URLs (n8n에서 호출할 로컬 엔드포인트)
    LOCAL_API_HOST = os.getenv('LOCAL_API_HOST', 'localhost')
    LOCAL_API_PORT = os.getenv('LOCAL_API_PORT', '8000')
    
    # 워크플로우 ID (n8n에서 생성된 워크플로우 ID)
    MAIN_TRADING_WORKFLOW_ID = os.getenv('MAIN_TRADING_WORKFLOW_ID', '')
    KIWOOM_TRADING_WORKFLOW_ID = os.getenv('KIWOOM_TRADING_WORKFLOW_ID', '')
    MONITORING_WORKFLOW_ID = os.getenv('MONITORING_WORKFLOW_ID', '')
    
    @classmethod
    def get_n8n_url(cls):
        """n8n 서버 URL 반환"""
        return f"{cls.N8N_PROTOCOL}://{cls.N8N_HOST}:{cls.N8N_PORT}"
    
    @classmethod
    def get_webhook_url(cls, workflow_id: str):
        """n8n 웹훅 URL 반환"""
        return f"{cls.get_n8n_url()}/webhook/{workflow_id}"
    
    @classmethod
    def get_local_api_url(cls):
        """로컬 API URL 반환"""
        return f"http://{cls.LOCAL_API_HOST}:{cls.LOCAL_API_PORT}"