"""
키움증권 WebSocket 클라이언트
실시간 잔고 조회 (모의투자 지원)
"""

import os
import json
import asyncio
import websockets
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KiwoomWebSocketClient:
    """키움증권 WebSocket 클라이언트 (잔고 실시간 조회)"""

    def __init__(self, on_balance_update: Optional[Callable] = None):
        """
        Args:
            on_balance_update: 잔고 업데이트 콜백 함수 (data: dict)
        """
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

        # WebSocket URL
        if self.is_demo:
            self.ws_url = "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"
        else:
            self.ws_url = "wss://api.kiwoom.com:10000/api/dostk/websocket"

        self.access_token = None
        self.websocket = None
        self.is_connected = False
        self.on_balance_update = on_balance_update

        logger.info(f"[KiwoomWS] Initialized - URL: {self.ws_url}, Account: {self.account_no}")

    async def _get_access_token(self) -> str:
        """OAuth 2.0 액세스 토큰 발급 (REST API 사용)"""
        import aiohttp

        if self.is_demo:
            token_url = "https://mockapi.kiwoom.com/oauth2/token"
        else:
            token_url = "https://openapi.kiwoom.com:9443/oauth2/token"

        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "secretkey": self.app_secret
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"토큰 발급 실패: {error_text}")

                result = await response.json()

                # 다양한 응답 형식 지원
                token = result.get('access_token') or result.get('token') or result.get('accessToken')
                if not token:
                    raise Exception(f"토큰을 찾을 수 없음: {result}")

                logger.info(f"[KiwoomWS] Access token obtained: {token[:20]}...")
                return token

    async def connect(self):
        """WebSocket 연결"""
        try:
            # 1. Access Token 발급
            self.access_token = await self._get_access_token()

            # 2. WebSocket 연결
            logger.info(f"[KiwoomWS] Connecting to {self.ws_url}...")

            # WebSocket 헤더 설정
            headers = {
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }

            self.websocket = await websockets.connect(
                self.ws_url,
                additional_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )

            self.is_connected = True
            logger.info("[KiwoomWS] ✅ WebSocket connected")

            # 3. 잔고 실시간 등록 (API ID: 04)
            await self._register_balance()

        except Exception as e:
            logger.error(f"[KiwoomWS] ❌ Connection failed: {e}")
            raise

    async def _register_balance(self):
        """잔고(04) 실시간 등록"""
        register_msg = {
            "trnm": "REG",          # 등록
            "grp_no": "1",          # 그룹번호
            "refresh": "1",         # 기존 등록 유지
            "data": [
                {
                    "item": [""],   # 종목코드 (잔고는 빈 문자열)
                    "type": ["04"]  # 04: 잔고
                }
            ]
        }

        await self.websocket.send(json.dumps(register_msg))
        logger.info(f"[KiwoomWS] 📡 잔고(04) 등록 요청: {register_msg}")

        # 등록 응답 대기
        response = await self.websocket.recv()
        response_data = json.loads(response)
        logger.info(f"[KiwoomWS] 📨 등록 응답: {response_data}")

        if response_data.get('return_code') == 0:
            logger.info("[KiwoomWS] ✅ 잔고 등록 성공")
        else:
            logger.error(f"[KiwoomWS] ❌ 잔고 등록 실패: {response_data.get('return_msg')}")

    async def listen(self):
        """실시간 데이터 수신"""
        try:
            logger.info("[KiwoomWS] 📡 Listening for real-time data...")

            async for message in self.websocket:
                try:
                    data = json.loads(message)

                    # 실시간 데이터 수신 (trnm: REAL)
                    if data.get('trnm') == 'REAL':
                        await self._handle_real_data(data)
                    else:
                        logger.debug(f"[KiwoomWS] 기타 메시지: {data}")

                except json.JSONDecodeError as e:
                    logger.error(f"[KiwoomWS] JSON 파싱 오류: {e}, 메시지: {message}")
                except Exception as e:
                    logger.error(f"[KiwoomWS] 메시지 처리 오류: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("[KiwoomWS] ⚠️ Connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"[KiwoomWS] ❌ Listen error: {e}")
            self.is_connected = False

    async def _handle_real_data(self, data: Dict[str, Any]):
        """실시간 잔고 데이터 처리"""
        try:
            logger.info(f"[KiwoomWS] 📊 실시간 잔고 데이터 수신: {json.dumps(data, ensure_ascii=False)}")

            # data 리스트에서 잔고 정보 추출
            if 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    if item.get('type') == '04' and item.get('name') == '현물잔고':
                        balance_data = self._parse_balance_data(item.get('values', {}))

                        # 콜백 함수 호출
                        if self.on_balance_update:
                            await self.on_balance_update(balance_data)

        except Exception as e:
            logger.error(f"[KiwoomWS] 잔고 데이터 처리 오류: {e}")

    def _parse_balance_data(self, values: Dict[str, str]) -> Dict[str, Any]:
        """
        WebSocket 응답을 DB 저장 형식으로 변환

        필드 매핑:
        - 9201: 계좌번호
        - 9001: 종목코드
        - 302: 종목명
        - 10: 현재가
        - 930: 보유수량
        - 931: 매입단가
        - 932: 총매입가
        - 933: 주문가능수량
        - 8019: 손익률
        """
        return {
            "account_number": values.get('9201', ''),
            "stock_code": values.get('9001', ''),
            "stock_name": values.get('302', ''),
            "current_price": int(values.get('10', 0)),
            "quantity": int(values.get('930', 0)),
            "avg_price": int(values.get('931', 0)),
            "total_purchase": int(values.get('932', 0)),
            "available_qty": int(values.get('933', 0)),
            "profit_loss_rate": float(values.get('8019', 0.0)),
            "timestamp": datetime.now().isoformat()
        }

    async def disconnect(self):
        """WebSocket 연결 해제"""
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
            logger.info("[KiwoomWS] 🔌 Disconnected")

    async def run(self):
        """WebSocket 클라이언트 실행 (자동 재연결)"""
        while True:
            try:
                await self.connect()
                await self.listen()
            except Exception as e:
                logger.error(f"[KiwoomWS] ❌ Error: {e}")
                self.is_connected = False

            # 재연결 대기
            if not self.is_connected:
                logger.info("[KiwoomWS] 🔄 Reconnecting in 10 seconds...")
                await asyncio.sleep(10)


# 싱글톤 인스턴스
_websocket_client = None


def get_websocket_client(on_balance_update: Optional[Callable] = None) -> KiwoomWebSocketClient:
    """WebSocket 클라이언트 싱글톤"""
    global _websocket_client
    if _websocket_client is None:
        _websocket_client = KiwoomWebSocketClient(on_balance_update)
    return _websocket_client
