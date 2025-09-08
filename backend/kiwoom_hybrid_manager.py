"""
키움증권 하이브리드 API 매니저
환경에 따라 OpenAPI+ 또는 REST API를 자동 선택
"""

import os
import sys
import platform
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 인터페이스 import
from kiwoom_api_interface import KiwoomAPIInterface

logger = logging.getLogger(__name__)
load_dotenv()

class KiwoomHybridManager:
    """
    환경에 따라 적절한 API를 자동 선택하는 매니저
    - Windows: OpenAPI+ 우선, 실패시 REST API
    - Linux/NAS: REST API만 사용
    """
    
    def __init__(self, prefer_api: str = None):
        """
        Args:
            prefer_api: 선호하는 API 타입 ('openapi', 'rest', None)
                       None인 경우 환경에 따라 자동 선택
        """
        self.api: Optional[KiwoomAPIInterface] = None
        self.prefer_api = prefer_api
        self.platform = self._detect_platform()
        self.available_apis = self._check_available_apis()
        
        logger.info(f"플랫폼: {self.platform}")
        logger.info(f"사용 가능한 API: {self.available_apis}")
        
    def _detect_platform(self) -> str:
        """플랫폼 감지"""
        system = platform.system().lower()
        
        # 시놀로지 NAS 감지
        if 'synology' in platform.platform().lower():
            return 'nas'
        elif system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'unknown'
    
    def _check_available_apis(self) -> Dict[str, bool]:
        """사용 가능한 API 확인"""
        available = {
            'openapi': False,
            'rest': False
        }
        
        # OpenAPI+ 확인 (Windows only)
        if self.platform == 'windows':
            try:
                import win32com.client
                # 기존 OpenAPI+ 모듈 확인
                test = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
                available['openapi'] = True
                logger.info("OpenAPI+ 사용 가능")
            except Exception as e:
                logger.warning(f"OpenAPI+ 사용 불가: {e}")
        
        # REST API 확인 (모든 플랫폼)
        if os.getenv('KIWOOM_APP_KEY') and os.getenv('KIWOOM_APP_SECRET'):
            available['rest'] = True
            logger.info("REST API 사용 가능")
        else:
            logger.warning("REST API 키가 설정되지 않음")
        
        return available
    
    async def initialize(self, force_api: str = None) -> bool:
        """
        API 초기화
        
        Args:
            force_api: 강제로 특정 API 사용 ('openapi' or 'rest')
        
        Returns:
            성공 여부
        """
        api_type = force_api or self.prefer_api
        
        # API 타입이 지정되지 않은 경우 자동 선택
        if not api_type:
            if self.platform == 'windows' and self.available_apis['openapi']:
                # Windows에서는 OpenAPI+ 우선
                api_type = 'openapi'
            elif self.available_apis['rest']:
                # 그 외 환경 또는 OpenAPI+ 불가시 REST API
                api_type = 'rest'
            else:
                logger.error("사용 가능한 API가 없습니다")
                return False
        
        # 선택된 API 타입 확인
        if not self.available_apis.get(api_type, False):
            logger.error(f"{api_type} API를 사용할 수 없습니다")
            
            # 대체 API 시도
            if api_type == 'openapi' and self.available_apis['rest']:
                logger.info("REST API로 대체 시도")
                api_type = 'rest'
            else:
                return False
        
        # API 인스턴스 생성
        try:
            if api_type == 'openapi':
                from kiwoom_openapi_impl import KiwoomOpenAPI
                self.api = KiwoomOpenAPI()
            else:  # rest
                from kiwoom_rest_impl import KiwoomRestAPI
                self.api = KiwoomRestAPI()
            
            # 연결
            success = await self.api.connect()
            if success:
                logger.info(f"{api_type.upper()} API 초기화 성공")
                return True
            else:
                logger.error(f"{api_type.upper()} API 초기화 실패")
                
                # OpenAPI+ 실패시 REST API로 재시도
                if api_type == 'openapi' and self.available_apis['rest']:
                    logger.info("REST API로 재시도")
                    return await self.initialize(force_api='rest')
                
                return False
                
        except Exception as e:
            logger.error(f"API 초기화 오류: {e}")
            
            # 오류 발생시 대체 API 시도
            if api_type == 'openapi' and self.available_apis['rest']:
                logger.info("REST API로 재시도")
                return await self.initialize(force_api='rest')
            
            return False
    
    def get_api(self) -> Optional[KiwoomAPIInterface]:
        """현재 API 인스턴스 반환"""
        return self.api
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        status = {
            'platform': self.platform,
            'available_apis': self.available_apis,
            'current_api': None,
            'is_connected': False
        }
        
        if self.api:
            status['current_api'] = self.api.api_type
            status['is_connected'] = self.api.is_connected
            status['api_info'] = self.api.get_api_info()
        
        return status
    
    async def switch_api(self, new_api_type: str) -> bool:
        """
        API 전환
        
        Args:
            new_api_type: 'openapi' or 'rest'
        
        Returns:
            전환 성공 여부
        """
        if not self.available_apis.get(new_api_type, False):
            logger.error(f"{new_api_type} API는 사용할 수 없습니다")
            return False
        
        # 기존 API 연결 해제
        if self.api:
            await self.api.disconnect()
            self.api = None
        
        # 새 API로 초기화
        return await self.initialize(force_api=new_api_type)


# 싱글톤 인스턴스
_manager_instance = None

def get_kiwoom_manager() -> KiwoomHybridManager:
    """싱글톤 매니저 인스턴스 반환"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = KiwoomHybridManager()
    return _manager_instance


# 사용 예제
async def example_usage():
    """하이브리드 매니저 사용 예제"""
    
    # 1. 매니저 초기화 (자동 선택)
    manager = get_kiwoom_manager()
    
    # 2. API 초기화
    success = await manager.initialize()
    if not success:
        logger.error("API 초기화 실패")
        return
    
    # 3. API 사용
    api = manager.get_api()
    if api:
        # 현재가 조회
        price = await api.get_current_price('005930')
        if price:
            logger.info(f"삼성전자 현재가: {price.price:,}원")
        
        # 잔고 조회
        balance = await api.get_balance()
        if balance:
            logger.info(f"계좌 잔고: {balance.cash:,}원")
        
        # 상태 확인
        status = manager.get_status()
        logger.info(f"현재 API: {status['current_api']}")
        logger.info(f"플랫폼: {status['platform']}")
    
    # 4. API 전환 (필요시)
    if manager.available_apis['rest']:
        success = await manager.switch_api('rest')
        if success:
            logger.info("REST API로 전환 성공")


if __name__ == "__main__":
    import asyncio
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 실행
    asyncio.run(example_usage())