"""
키움증권 API 공통 인터페이스
OpenAPI+와 REST API를 추상화하여 동일한 인터페이스로 사용 가능
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class StockPrice:
    """주식 가격 정보"""
    code: str
    name: str
    price: int
    change: int
    change_rate: float
    volume: int
    high: int
    low: int
    open: int
    timestamp: datetime

@dataclass
class OrderResult:
    """주문 결과"""
    success: bool
    order_no: str
    message: str
    timestamp: datetime
    details: Dict[str, Any]

@dataclass
class Balance:
    """계좌 잔고"""
    total_eval: int  # 총평가금액
    total_purchase: int  # 총매입금액
    total_profit: int  # 총손익
    cash: int  # 예수금
    holdings: List[Dict[str, Any]]  # 보유종목
    timestamp: datetime

class KiwoomAPIInterface(ABC):
    """키움증권 API 공통 인터페이스"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """API 연결"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """API 연결 해제"""
        pass
    
    @abstractmethod
    async def get_current_price(self, stock_code: str) -> Optional[StockPrice]:
        """현재가 조회"""
        pass
    
    @abstractmethod
    async def get_ohlcv(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """일봉 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Optional[Balance]:
        """계좌 잔고 조회"""
        pass
    
    @abstractmethod
    async def place_order(
        self, 
        stock_code: str, 
        quantity: int, 
        price: int, 
        order_type: str = 'buy',
        order_method: str = 'limit'
    ) -> Optional[OrderResult]:
        """주문 실행
        order_type: 'buy' or 'sell'
        order_method: 'limit' or 'market'
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_no: str) -> Optional[OrderResult]:
        """주문 취소"""
        pass
    
    @abstractmethod
    async def get_order_history(self, start_date: str = None) -> List[Dict]:
        """주문 내역 조회"""
        pass
    
    @abstractmethod
    async def subscribe_realtime(self, stock_codes: List[str], callback: callable):
        """실시간 시세 구독"""
        pass
    
    @abstractmethod
    async def unsubscribe_realtime(self, stock_codes: List[str]):
        """실시간 시세 구독 해제"""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        pass
    
    @property
    @abstractmethod
    def api_type(self) -> str:
        """API 타입 반환 ('openapi' or 'rest')"""
        pass
    
    @property
    @abstractmethod
    def platform(self) -> str:
        """플랫폼 반환 ('windows', 'linux', 'nas')"""
        pass
    
    def get_api_info(self) -> Dict[str, Any]:
        """API 정보 반환"""
        return {
            'api_type': self.api_type,
            'platform': self.platform,
            'is_connected': self.is_connected,
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> bool:
        """API 상태 체크"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # 삼성전자로 테스트
            price = await self.get_current_price('005930')
            return price is not None
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False