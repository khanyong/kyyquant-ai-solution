"""
클라우드 기반 전략 실행자 - 모든 사용자의 전략을 중앙에서 실행
"""
import asyncio
from datetime import datetime, time
from typing import Dict, Any, List
import os
from supabase import create_client
from dotenv import load_dotenv
import aiohttp
import json

load_dotenv()

class CloudStrategyExecutor:
    """
    클라우드에서 모든 사용자의 전략을 실행하는 중앙 실행자
    Railway, Render, AWS Lambda 등에서 24/7 실행
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Service key for admin access
        self.client = create_client(self.supabase_url, self.supabase_key)
        
        # 한국투자 API 엔드포인트
        self.api_base_url = os.getenv('KIS_API_URL', 'https://openapi.koreainvestment.com:9443')
        
    async def run_forever(self):
        """메인 실행 루프 - 24/7 실행"""
        print("🚀 Cloud Strategy Executor started")
        
        while True:
            try:
                # 1. 시장 개장 시간 체크
                if self.is_market_open():
                    # 2. 활성화된 모든 전략 조회
                    active_strategies = await self.get_active_strategies()
                    print(f"Found {len(active_strategies)} active strategies")
                    
                    # 3. 각 사용자의 전략을 병렬로 실행
                    tasks = []
                    for strategy in active_strategies:
                        task = asyncio.create_task(
                            self.execute_user_strategy(strategy)
                        )
                        tasks.append(task)
                    
                    # 모든 전략 실행 완료 대기
                    if tasks:
                        await asyncio.gather(*tasks)
                    
                # 1분 대기 후 다시 체크
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(60)
    
    def is_market_open(self) -> bool:
        """한국 시장 개장 시간 체크"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()
        
        # 월-금 (0-4)
        if weekday >= 5:  # 토, 일
            return False
        
        # 09:00 - 15:30
        market_open = time(9, 0)
        market_close = time(15, 30)
        
        return market_open <= current_time <= market_close
    
    async def get_active_strategies(self) -> List[Dict[str, Any]]:
        """모든 활성 전략 조회"""
        try:
            response = self.client.table('strategies_v2').select(
                '''
                id, user_id, name, version, 
                indicators, entry_conditions, exit_conditions,
                risk_management, universe, strategy_code,
                user:users!user_id(
                    id, email, 
                    api_credentials:user_api_credentials(
                        api_key, api_secret, account_no
                    )
                )
                '''
            ).eq('is_active', True).eq('auto_trade_enabled', True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting active strategies: {e}")
            return []
    
    async def execute_user_strategy(self, strategy: Dict[str, Any]):
        """개별 사용자 전략 실행"""
        try:
            user_id = strategy['user_id']
            strategy_id = strategy['id']
            
            print(f"Executing strategy {strategy['name']} for user {user_id}")
            
            # 1. 사용자 API 인증 정보 가져오기
            user_creds = strategy['user']['api_credentials'][0] if strategy['user'].get('api_credentials') else None
            
            if not user_creds:
                print(f"No API credentials for user {user_id}")
                return
            
            # 2. 시장 데이터 가져오기
            market_data = await self.fetch_market_data(
                strategy['universe'],
                user_creds
            )
            
            # 3. 전략 코드 실행
            signal = await self.run_strategy_code(
                strategy['strategy_code'],
                market_data,
                strategy
            )
            
            # 4. 신호 기록
            await self.log_signal(strategy_id, user_id, signal)
            
            # 5. 리스크 체크
            if signal['type'] in ['buy', 'sell']:
                risk_check = await self.check_risk_limits(user_id, signal)
                
                if risk_check['passed']:
                    # 6. 주문 실행
                    order_result = await self.place_order(
                        user_creds,
                        signal,
                        strategy_id
                    )
                    
                    # 7. 주문 결과 기록
                    await self.log_order(user_id, strategy_id, order_result)
                else:
                    print(f"Risk check failed: {risk_check['reason']}")
            
        except Exception as e:
            print(f"Error executing strategy {strategy.get('name')}: {e}")
            await self.log_error(strategy['id'], str(e))
    
    async def fetch_market_data(self, universe: List[str], creds: Dict) -> Dict[str, Any]:
        """사용자별 API 키로 시장 데이터 조회"""
        market_data = {}
        
        headers = {
            'authorization': f"Bearer {creds['api_key']}",
            'appkey': creds['api_key'],
            'appsecret': creds['api_secret'],
            'tr_id': 'FHKST01010100'  # 주식 현재가 조회
        }
        
        async with aiohttp.ClientSession() as session:
            for stock_code in universe:
                try:
                    # 한국투자 API 호출
                    url = f"{self.api_base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
                    params = {
                        'fid_cond_mrkt_div_code': 'J',
                        'fid_input_iscd': stock_code
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            market_data[stock_code] = data['output']
                            
                except Exception as e:
                    print(f"Error fetching data for {stock_code}: {e}")
        
        return market_data
    
    async def run_strategy_code(self, code: str, market_data: Dict, 
                               strategy_config: Dict) -> Dict[str, Any]:
        """전략 코드 실행 (샌드박스)"""
        try:
            # 동적으로 전략 코드 실행
            exec_globals = {
                'market_data': market_data,
                'indicators': strategy_config['indicators'],
                'entry_conditions': strategy_config['entry_conditions'],
                'exit_conditions': strategy_config['exit_conditions']
            }
            
            exec(code, exec_globals)
            
            # 전략 함수 호출
            if 'calculate_signal' in exec_globals:
                signal = exec_globals['calculate_signal'](market_data)
                return signal
            else:
                return {'type': 'hold', 'reason': 'No signal function found'}
                
        except Exception as e:
            print(f"Error running strategy code: {e}")
            return {'type': 'hold', 'reason': f'Error: {str(e)}'}
    
    async def check_risk_limits(self, user_id: str, signal: Dict) -> Dict[str, Any]:
        """사용자별 리스크 한도 체크"""
        try:
            # 오늘의 거래 횟수 체크
            today = datetime.now().strftime('%Y-%m-%d')
            trades_response = self.client.table('orders').select('id').eq(
                'user_id', user_id
            ).gte('created_at', f"{today}T00:00:00").execute()
            
            trades_today = len(trades_response.data) if trades_response.data else 0
            
            if trades_today >= 10:  # 일일 거래 한도
                return {'passed': False, 'reason': 'Daily trade limit exceeded'}
            
            # 포지션 수 체크
            positions_response = self.client.table('portfolio').select('id').eq(
                'user_id', user_id
            ).gt('quantity', 0).execute()
            
            positions = len(positions_response.data) if positions_response.data else 0
            
            if signal['type'] == 'buy' and positions >= 5:  # 최대 5개 종목
                return {'passed': False, 'reason': 'Max positions reached'}
            
            return {'passed': True, 'reason': 'OK'}
            
        except Exception as e:
            print(f"Error checking risk limits: {e}")
            return {'passed': False, 'reason': str(e)}
    
    async def place_order(self, creds: Dict, signal: Dict, strategy_id: int) -> Dict:
        """한국투자 API로 실제 주문 실행"""
        try:
            headers = {
                'authorization': f"Bearer {creds['api_key']}",
                'appkey': creds['api_key'],
                'appsecret': creds['api_secret'],
                'tr_id': 'TTTT1002U' if signal['type'] == 'buy' else 'TTTT1006U'  # 매수/매도
            }
            
            body = {
                'CANO': creds['account_no'][:8],
                'ACNT_PRDT_CD': creds['account_no'][8:],
                'PDNO': signal['stock_code'],
                'ORD_DVSN': '01',  # 지정가
                'ORD_QTY': str(signal['quantity']),
                'ORD_UNPR': str(signal['price'])
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/uapi/domestic-stock/v1/trading/order-cash"
                
                async with session.post(url, headers=headers, json=body) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'order_no': result['output']['ODNO'],
                            'message': result['msg1']
                        }
                    else:
                        return {
                            'success': False,
                            'message': f"Order failed: {response.status}"
                        }
                        
        except Exception as e:
            print(f"Error placing order: {e}")
            return {'success': False, 'message': str(e)}
    
    async def log_signal(self, strategy_id: int, user_id: str, signal: Dict):
        """신호 기록"""
        try:
            signal_data = {
                'strategy_id': strategy_id,
                'user_id': user_id,
                'signal_type': signal.get('type', 'hold'),
                'stock_code': signal.get('stock_code'),
                'strength': signal.get('strength', 0),
                'price': signal.get('price'),
                'notes': signal.get('reason'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.table('signals').insert(signal_data).execute()
        except Exception as e:
            print(f"Error logging signal: {e}")
    
    async def log_order(self, user_id: str, strategy_id: int, order_result: Dict):
        """주문 기록"""
        try:
            order_data = {
                'user_id': user_id,
                'strategy_id': strategy_id,
                'order_id': order_result.get('order_no'),
                'status': 'success' if order_result.get('success') else 'failed',
                'message': order_result.get('message'),
                'created_at': datetime.now().isoformat()
            }
            
            self.client.table('orders').insert(order_data).execute()
        except Exception as e:
            print(f"Error logging order: {e}")
    
    async def log_error(self, strategy_id: int, error_message: str):
        """에러 로그"""
        try:
            self.client.table('system_logs').insert({
                'level': 'ERROR',
                'module': 'CloudExecutor',
                'message': error_message,
                'details': {'strategy_id': strategy_id},
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error logging error: {e}")


# 배포용 메인 함수
async def main():
    """클라우드에서 실행될 메인 함수"""
    executor = CloudStrategyExecutor()
    await executor.run_forever()

if __name__ == "__main__":
    asyncio.run(main())