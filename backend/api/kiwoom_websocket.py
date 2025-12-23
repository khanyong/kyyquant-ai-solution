"""
키움증권 WebSocket 클라이언트
실시간 잔고 조회 (모의투자 지원)
"""

import os
import json
import asyncio
import websockets
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
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

        # Supabase Client (For DB-based holiday check)
        self.supabase = None
        try:
            sb_url = os.getenv('SUPABASE_URL')
            sb_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
            if sb_url and sb_key:
                from supabase import create_client
                self.supabase = create_client(sb_url, sb_key)
        except Exception as e:
            logger.warning(f"[KiwoomWS] Supabase connection failed (Holiday check will use local fallback): {e}")

        logger.info(f"[KiwoomWS] Initialized - URL: {self.ws_url}, Account: {self.account_no}")

    async def _get_access_token(self) -> str:
        """OAuth 2.0 액세스 토큰 발급 (TokenManager 사용)"""
        from .token_manager import get_token_manager
        
        loop = asyncio.get_event_loop()
        # Blocking call to TokenManager within executor
        token = await loop.run_in_executor(None, get_token_manager(self.is_demo).get_token)
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
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )

            self.is_connected = True
            logger.info("[KiwoomWS] ✅ WebSocket connected")

            # 3. 잔고 실시간 등록 (API ID: 04)
            logger.info("[KiwoomWS] ⏳ Waiting for server authentication...")
            await asyncio.sleep(3.0)  # 로그인 처리 대기 (1s -> 3s)
            
            # 연결 상태 재확인
            if self.is_connected:
                await self._register_balance()

        except Exception as e:
            logger.error(f"[KiwoomWS] ❌ Connection failed: {e}")
            raise

    async def _register_balance(self):
        """잔고(04) 실시간 등록"""
        if not self.websocket or not self.is_connected:
            return

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

        try:
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
        except Exception as e:
            logger.error(f"[KiwoomWS] 잔고 등록 중 오류: {e}")

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

    def _is_holiday(self, date_str: str) -> bool:
        """공휴일 체크 (Supabase or Hardcoded)"""
        # 1. DB Check if available
        if self.supabase:
            try:
                # public_holidays 테이블이 있다고 가정 (date 컬럼)
                res = self.supabase.table('public_holidays').select('date').eq('date', date_str).execute()
                if res.data:
                    return True
            except Exception:
                # 테이블이 없거나 에러 시 무시하고 하드코딩 체크
                pass

        # 2. Hardcoded fallback (2025 major holidays)
        # TODO: 매년 업데이트 필요 or DB 연동 필수
        holidays_2025 = {
            '2025-01-01', # 신정
            '2025-01-27', '2025-01-28', '2025-01-29', '2025-01-30', # 설날 연휴
            '2025-03-03', # 삼일절 대체공휴일(3.1 토)
            '2025-05-05', # 어린이날
            '2025-05-06', # 석가탄신일
            '2025-06-06', # 현충일
            '2025-08-15', # 광복절
            '2025-10-03', # 개천절
            '2025-10-06', '2025-10-07', '2025-10-08', # 추석 (가정)
            '2025-10-09', # 한글날
            '2025-12-25'  # 성탄절
        }
        
        return date_str in holidays_2025

    def _is_market_open(self) -> bool:
        """장 운영 시간 확인 (평일 08:30 ~ 16:00 KST, 공휴일 제외)"""
        # UTC -> KST 변환
        now_utc = datetime.utcnow()
        korea_time = now_utc + timedelta(hours=9)
        
        # 주말 체크 (5:토, 6:일)
        if korea_time.weekday() >= 5:
            return False
            
        # 공휴일 체크
        today_str = korea_time.strftime('%Y-%m-%d')
        if self._is_holiday(today_str):
            logger.info(f"[KiwoomWS] 🏖️ 오늘은 공휴일({today_str})입니다.")
            return False
            
        # 시간 체크 (HHMM)
        current_hm = korea_time.hour * 100 + korea_time.minute
        # 08:30 ~ 16:00 (장전/장후 동시호가 포함 넉넉하게)
        return 830 <= current_hm <= 1600

    async def run(self):
        """WebSocket 클라이언트 실행 (자동 재연결)"""
        while True:
            # 장 운영 시간 체크
            if not self._is_market_open():
                logger.info("[KiwoomWS] 🌜 장 마감 시간입니다. (08:30 ~ 16:00 KST 외/주말). 연결을 일시 중단합니다.")
                await asyncio.sleep(600)  # 10분 대기
                continue

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
