"""
키움 OpenAPI+ WebSocket 브리지 서버
실시간 데이터를 WebSocket으로 브로드캐스트하고 Supabase에 저장
"""

import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
import websockets
from websockets.server import WebSocketServerProtocol
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from scripts.kiwoom.kiwoom_api import KiwoomAPI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiwoomThread(QThread):
    """키움 API를 별도 스레드에서 실행"""
    data_received = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.api = None
        self.watched_stocks = []
        self.account_no = None
        
    def run(self):
        """스레드 실행"""
        self.api = KiwoomAPI()
        
        # 로그인
        if self.api.comm_connect():
            logger.info("키움 API 로그인 성공")
            
            # 계좌 정보 가져오기
            accounts = self.api.get_account_list()
            if accounts:
                self.account_no = accounts[0]
                logger.info(f"계좌번호: {self.account_no}")
                
                # 초기 잔고 조회
                self.api.request_balance(self.account_no)
            
            # 이벤트 루프 실행
            self.api.app.exec_()
        else:
            logger.error("키움 API 로그인 실패")
    
    def add_stock_monitoring(self, stock_code: str):
        """실시간 모니터링 종목 추가"""
        if stock_code not in self.watched_stocks:
            self.watched_stocks.append(stock_code)
            if self.api and self.api.connected:
                # 실시간 데이터 등록
                fid_list = "10;11;12;13;14;15;16;17;18;20"  # 현재가, 전일대비, 등락율, 거래량 등
                self.api.set_real_reg(f"100{len(self.watched_stocks)}", stock_code, fid_list, "1")
                logger.info(f"실시간 모니터링 추가: {stock_code}")
    
    def remove_stock_monitoring(self, stock_code: str):
        """실시간 모니터링 종목 제거"""
        if stock_code in self.watched_stocks:
            self.watched_stocks.remove(stock_code)
            logger.info(f"실시간 모니터링 제거: {stock_code}")
    
    def request_stock_info(self, stock_code: str):
        """주식 정보 요청"""
        if self.api and self.api.connected:
            self.api.request_stock_info(stock_code)
    
    def send_order(self, order_data: dict):
        """주문 전송"""
        if self.api and self.api.connected:
            result = self.api.send_order(
                rq_name=order_data.get('rq_name', '주문'),
                screen_no="5000",
                acc_no=self.account_no,
                order_type=order_data['order_type'],
                code=order_data['stock_code'],
                qty=order_data['quantity'],
                price=order_data['price'],
                hoga_gb=order_data.get('hoga_gb', '00')  # 00: 지정가, 03: 시장가
            )
            return result == 0


class WebSocketBridge:
    """WebSocket 서버 및 Supabase 연동"""
    
    def __init__(self):
        self.clients: List[WebSocketServerProtocol] = []
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL', ''),
            os.getenv('SUPABASE_ANON_KEY', '')
        )
        self.kiwoom_thread = None
        
    async def register(self, websocket: WebSocketServerProtocol):
        """클라이언트 등록"""
        self.clients.append(websocket)
        logger.info(f"클라이언트 연결: {websocket.remote_address}")
        
    async def unregister(self, websocket: WebSocketServerProtocol):
        """클라이언트 해제"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"클라이언트 연결 해제: {websocket.remote_address}")
    
    async def broadcast(self, message: dict):
        """모든 클라이언트에게 메시지 브로드캐스트"""
        if self.clients:
            message_str = json.dumps(message, ensure_ascii=False)
            await asyncio.gather(
                *[client.send(message_str) for client in self.clients],
                return_exceptions=True
            )
    
    async def save_to_supabase(self, table: str, data: dict):
        """Supabase에 데이터 저장"""
        try:
            result = self.supabase.table(table).insert(data).execute()
            logger.info(f"Supabase 저장 성공: {table}")
            return result
        except Exception as e:
            logger.error(f"Supabase 저장 실패: {e}")
            return None
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """클라이언트 요청 처리"""
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_client_message(data, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def process_client_message(self, data: dict, websocket: WebSocketServerProtocol):
        """클라이언트 메시지 처리"""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # 실시간 데이터 구독
            stock_code = data.get('stock_code')
            if stock_code and self.kiwoom_thread:
                self.kiwoom_thread.add_stock_monitoring(stock_code)
                await websocket.send(json.dumps({
                    'type': 'subscribe_success',
                    'stock_code': stock_code
                }))
        
        elif msg_type == 'unsubscribe':
            # 실시간 데이터 구독 해제
            stock_code = data.get('stock_code')
            if stock_code and self.kiwoom_thread:
                self.kiwoom_thread.remove_stock_monitoring(stock_code)
                await websocket.send(json.dumps({
                    'type': 'unsubscribe_success',
                    'stock_code': stock_code
                }))
        
        elif msg_type == 'order':
            # 주문 요청
            if self.kiwoom_thread:
                result = self.kiwoom_thread.send_order(data['order_data'])
                await websocket.send(json.dumps({
                    'type': 'order_result',
                    'success': result,
                    'order_data': data['order_data']
                }))
                
                # 주문 내역 Supabase 저장
                if result:
                    await self.save_to_supabase('orders', {
                        'stock_code': data['order_data']['stock_code'],
                        'order_type': data['order_data']['order_type'],
                        'quantity': data['order_data']['quantity'],
                        'price': data['order_data']['price'],
                        'status': 'pending',
                        'created_at': datetime.now().isoformat()
                    })
        
        elif msg_type == 'get_balance':
            # 잔고 조회
            if self.kiwoom_thread:
                self.kiwoom_thread.api.request_balance(self.kiwoom_thread.account_no)
    
    def on_kiwoom_data(self, data: dict):
        """키움 API로부터 데이터 수신"""
        asyncio.create_task(self.process_kiwoom_data(data))
    
    async def process_kiwoom_data(self, data: dict):
        """키움 데이터 처리 및 브로드캐스트"""
        data_type = data.get('type')
        
        if data_type == 'real_stock':
            # 실시간 주식 데이터
            await self.broadcast({
                'type': 'stock_update',
                'data': data['data']
            })
            
            # Supabase에 저장
            await self.save_to_supabase('stock_prices', {
                'stock_code': data['data']['stock_code'],
                'current_price': data['data']['current_price'],
                'change': data['data']['change'],
                'change_rate': data['data']['change_rate'],
                'volume': data['data']['volume'],
                'timestamp': datetime.now().isoformat()
            })
        
        elif data_type == 'balance':
            # 잔고 데이터
            await self.broadcast({
                'type': 'balance_update',
                'data': data['data']
            })
            
            # Supabase에 포트폴리오 업데이트
            for item in data['data']:
                await self.save_to_supabase('portfolio', {
                    'stock_code': item['stock_code'],
                    'stock_name': item['stock_name'],
                    'quantity': item['quantity'],
                    'avg_price': item['avg_price'],
                    'current_price': item['current_price'],
                    'profit_loss': item['profit_loss'],
                    'profit_rate': item['profit_rate'],
                    'updated_at': datetime.now().isoformat()
                })
        
        elif data_type == 'order_execution':
            # 주문 체결
            await self.broadcast({
                'type': 'order_executed',
                'data': data['data']
            })
            
            # 주문 상태 업데이트
            await self.supabase.table('orders').update({
                'status': 'executed',
                'executed_at': datetime.now().isoformat()
            }).eq('order_id', data['data']['order_id']).execute()
    
    async def start_server(self, host='localhost', port=8765):
        """WebSocket 서버 시작"""
        logger.info(f"WebSocket 서버 시작: ws://{host}:{port}")
        
        # 키움 스레드 시작
        self.kiwoom_thread = KiwoomThread()
        self.kiwoom_thread.data_received.connect(self.on_kiwoom_data)
        self.kiwoom_thread.start()
        
        # WebSocket 서버 실행
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # 무한 대기


async def main():
    """메인 함수"""
    bridge = WebSocketBridge()
    await bridge.start_server()


if __name__ == "__main__":
    # QApplication은 메인 스레드에서 실행되어야 함
    app = QApplication(sys.argv)
    
    # 비동기 이벤트 루프 실행
    asyncio.run(main())