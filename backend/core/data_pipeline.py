"""
API 데이터를 Supabase로 전송하는 파이프라인
"""
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from database.database_supabase import SupabaseDatabase
from config.config import config
import json

class DataPipeline:
    """API 데이터 처리 및 저장 파이프라인"""
    
    def __init__(self):
        self.db = SupabaseDatabase()
        self.buffer = {
            'price_data': [],
            'orders': [],
            'signals': []
        }
        self.buffer_size = 100  # 버퍼 크기
        self.flush_interval = 5  # 5초마다 플러시
    
    async def process_realtime_data(self, data: Dict[str, Any]):
        """
        실시간 데이터 처리 흐름:
        1. KOA Studio/OpenAPI에서 실시간 체결 데이터 수신
        2. 데이터 검증 및 변환
        3. Supabase에 저장
        """
        
        # 1단계: 데이터 타입 확인
        data_type = data.get('type')
        
        if data_type == 'price':
            await self._process_price_data(data)
        elif data_type == 'order_execution':
            await self._process_order_execution(data)
        elif data_type == 'quote':
            await self._process_quote_data(data)
    
    async def _process_price_data(self, data: Dict[str, Any]):
        """
        가격 데이터 처리
        API 예시:
        {
            "type": "price",
            "stock_code": "005930",
            "timestamp": "2024-01-01T09:00:00",
            "price": 70000,
            "volume": 1000,
            "high": 71000,
            "low": 69000
        }
        """
        # 데이터 변환
        price_record = {
            'stock_code': data['stock_code'],
            'timestamp': data['timestamp'],
            'close': data['price'],
            'volume': data.get('volume', 0),
            'high': data.get('high'),
            'low': data.get('low'),
            'open': data.get('open')
        }
        
        # 버퍼에 추가
        self.buffer['price_data'].append(price_record)
        
        # 버퍼가 가득 차면 DB에 저장
        if len(self.buffer['price_data']) >= self.buffer_size:
            await self._flush_price_buffer()
    
    async def _flush_price_buffer(self):
        """가격 데이터 버퍼를 Supabase에 저장"""
        if self.buffer['price_data']:
            # 대량 삽입으로 성능 최적화
            count = self.db.bulk_insert_price_data(self.buffer['price_data'])
            print(f"Saved {count} price records to Supabase")
            self.buffer['price_data'] = []
    
    async def _process_order_execution(self, data: Dict[str, Any]):
        """
        주문 체결 데이터 처리
        API 예시:
        {
            "type": "order_execution",
            "order_id": "2024010100001",
            "stock_code": "005930",
            "executed_price": 70500,
            "executed_quantity": 10,
            "status": "executed"
        }
        """
        # 주문 상태 업데이트
        self.db.update_order_status(
            order_id=data['order_id'],
            status=data['status'],
            executed_price=data.get('executed_price'),
            executed_quantity=data.get('executed_quantity')
        )
        
        # 포트폴리오 업데이트
        if data['status'] == 'executed':
            order_type = 'buy' if data.get('order_type') == 'buy' else 'sell'
            quantity = data['executed_quantity'] if order_type == 'buy' else -data['executed_quantity']
            
            self.db.update_portfolio(
                stock_code=data['stock_code'],
                quantity=quantity,
                avg_price=data['executed_price'],
                current_price=data['executed_price']
            )
    
    async def _process_quote_data(self, data: Dict[str, Any]):
        """호가 데이터 처리 (실시간 모니터링용)"""
        # 호가 데이터는 주로 실시간 의사결정에 사용
        # 필요시 Redis 등 인메모리 DB에 저장
        pass
    
    async def periodic_flush(self):
        """주기적으로 버퍼 플러시"""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self._flush_price_buffer()


class StrategyExecutor:
    """전략 실행 및 관리"""
    
    def __init__(self):
        self.db = SupabaseDatabase()
        self.strategies = {}
        self.active_strategy = None
    
    def register_strategy(self, strategy):
        """
        전략 등록 프로세스:
        1. 전략 클래스 인스턴스 생성
        2. 파라미터 설정
        3. 메모리에 저장
        4. 설정은 config.json에 저장
        """
        self.strategies[strategy.name] = strategy
        
        # 전략 설정을 config에 저장
        config.set(f'strategy.custom.{strategy.name}', {
            'parameters': strategy.parameters,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        })
    
    async def execute_strategy(self, market_data: pd.DataFrame):
        """
        전략 실행 흐름:
        1. 시장 데이터 수신 (from API)
        2. 전략 신호 계산
        3. 리스크 검증
        4. 주문 생성
        5. Supabase에 기록
        """
        
        if not self.active_strategy:
            return
        
        # 1. 전략에서 신호 생성
        signal = self.active_strategy.calculate_signal(market_data)
        
        # 2. 신호를 Supabase에 저장
        signal_record = {
            'stock_code': signal.get('stock_code'),
            'signal_type': signal['type'],
            'strategy': self.active_strategy.name,
            'strength': signal.get('strength', 1.0),
            'price': signal.get('price'),
            'notes': signal.get('reason')
        }
        self.db.add_signal(signal_record)
        
        # 3. 신호가 'buy' 또는 'sell'인 경우 주문 생성
        if signal['type'] in ['buy', 'sell']:
            order = await self._create_order(signal)
            
            # 4. 주문을 Supabase에 저장
            order_record = {
                'order_id': order.get('order_id'),
                'stock_code': order['stock_code'],
                'order_type': order['order_type'],
                'quantity': order['quantity'],
                'price': order['price'],
                'order_method': order.get('order_method', 'limit'),
                'strategy': self.active_strategy.name,
                'status': 'pending'
            }
            self.db.add_order(order_record)
            
            # 5. API를 통해 실제 주문 전송
            # await send_order_to_api(order)
    
    async def _create_order(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """신호를 기반으로 주문 생성"""
        from core.risk_manager import risk_manager
        
        # 리스크 매니저로 포지션 크기 계산
        capital = 1000000  # 실제로는 API에서 가져옴
        position_size = risk_manager.calculate_position_size(signal, capital)
        
        return {
            'stock_code': signal.get('stock_code'),
            'order_type': signal['type'],
            'quantity': position_size,
            'price': signal.get('price'),
            'order_method': 'limit'
        }


# 데이터 흐름 예시
async def main_data_flow():
    """
    전체 데이터 흐름 예시:
    
    1. API → Backend: 실시간 데이터 수신
    2. Backend → Supabase: 데이터 저장
    3. Strategy → Signal: 전략 실행 및 신호 생성
    4. Signal → Order: 주문 생성
    5. Order → API: 주문 전송
    6. API → Supabase: 체결 결과 저장
    """
    
    pipeline = DataPipeline()
    executor = StrategyExecutor()
    
    # 모멘텀 전략 등록
    from strategies.momentum_strategy import MomentumStrategy
    momentum = MomentumStrategy()
    executor.register_strategy(momentum)
    executor.active_strategy = momentum
    
    # 실시간 데이터 시뮬레이션
    sample_data = {
        'type': 'price',
        'stock_code': '005930',
        'timestamp': datetime.now().isoformat(),
        'price': 70000,
        'volume': 1000,
        'high': 71000,
        'low': 69000
    }
    
    # 데이터 처리
    await pipeline.process_realtime_data(sample_data)
    
    # 전략 실행 (실제로는 충분한 데이터가 있어야 함)
    # market_data = pipeline.db.get_price_history('005930', days=30)
    # await executor.execute_strategy(market_data)

if __name__ == "__main__":
    asyncio.run(main_data_flow())