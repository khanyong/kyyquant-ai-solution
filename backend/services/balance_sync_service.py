"""
잔고 동기화 서비스
WebSocket으로 실시간 잔고 데이터를 받아 Supabase에 저장
"""

import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from supabase import create_client, Client

from api.kiwoom_websocket import get_websocket_client

logger = logging.getLogger(__name__)


class BalanceSyncService:
    """잔고 자동 동기화 서비스"""

    def __init__(self):
        # Supabase 클라이언트
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise Exception("Supabase credentials not configured")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.user_id = None  # 시스템 사용자 ID (환경변수에서 가져옴)

        logger.info("[BalanceSync] Service initialized")

    async def on_balance_update(self, balance_data: Dict[str, Any]):
        """
        WebSocket에서 잔고 데이터 수신 시 호출되는 콜백

        Args:
            balance_data: 잔고 정보 딕셔너리
        """
        try:
            logger.info(f"[BalanceSync] 📊 잔고 업데이트: {balance_data}")

            account_number = balance_data.get('account_number')
            stock_code = balance_data.get('stock_code')

            if not account_number:
                logger.warning("[BalanceSync] 계좌번호 없음, 스킵")
                return

            # 1. user_id 찾기 (계좌번호로 조회)
            if not self.user_id:
                user_id = await self._get_user_id_by_account(account_number)
                if not user_id:
                    logger.error(f"[BalanceSync] 계좌번호 {account_number}에 해당하는 사용자 없음")
                    return
                self.user_id = user_id

            # 2. 종목별 포트폴리오 업데이트
            if stock_code:
                await self._update_portfolio(balance_data)

            # 3. 계좌 총액 업데이트
            await self._update_account_balance()

            logger.info(f"[BalanceSync] ✅ DB 저장 완료: {stock_code or '계좌 총액'}")

        except Exception as e:
            logger.error(f"[BalanceSync] ❌ 잔고 저장 실패: {e}")

    async def _get_user_id_by_account(self, account_number: str) -> str:
        """계좌번호로 사용자 ID 찾기"""
        try:
            # 계좌번호 형식 정규화 (8112-5100-01 또는 8112-5100)
            normalized_account = account_number.replace('-', '')

            response = self.supabase.table('profiles').select('id').or_(
                f'kiwoom_account.eq.{account_number},'
                f'kiwoom_account.like.{normalized_account[:8]}-{normalized_account[8:]}%'
            ).limit(1).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]['id']

            return None

        except Exception as e:
            logger.error(f"[BalanceSync] 사용자 조회 실패: {e}")
            return None

    async def _update_portfolio(self, balance_data: Dict[str, Any]):
        """포트폴리오 테이블 업데이트 (종목별)"""
        try:
            portfolio_record = {
                'user_id': self.user_id,
                'account_number': balance_data['account_number'],
                'stock_code': balance_data['stock_code'],
                'stock_name': balance_data['stock_name'],
                'quantity': balance_data['quantity'],
                'available_quantity': balance_data['available_qty'],
                'average_price': balance_data['avg_price'],
                'current_price': balance_data['current_price'],
                'total_purchase_amount': balance_data['total_purchase'],
                'current_value': balance_data['quantity'] * balance_data['current_price'],
                'profit_loss': (balance_data['current_price'] - balance_data['avg_price']) * balance_data['quantity'],
                'profit_loss_rate': balance_data['profit_loss_rate'],
                'updated_at': datetime.now().isoformat()
            }

            # Upsert (있으면 업데이트, 없으면 삽입)
            self.supabase.table('kw_portfolio').upsert(
                portfolio_record,
                on_conflict='user_id,account_number,stock_code'
            ).execute()

        except Exception as e:
            logger.error(f"[BalanceSync] 포트폴리오 업데이트 실패: {e}")
            raise

    async def _update_account_balance(self):
        """계좌 총액 업데이트 (포트폴리오 합산)"""
        try:
            # RPC 함수 호출 (기존 로직 활용)
            account_number = os.getenv('KIWOOM_ACCOUNT_NO')

            self.supabase.rpc('update_account_totals', {
                'p_user_id': self.user_id,
                'p_account_number': account_number
            }).execute()

        except Exception as e:
            logger.error(f"[BalanceSync] 계좌 총액 업데이트 실패: {e}")
            raise

    async def start(self):
        """서비스 시작"""
        logger.info("[BalanceSync] 🚀 Starting balance sync service...")

        # WebSocket 클라이언트 생성 및 실행
        ws_client = get_websocket_client(on_balance_update=self.on_balance_update)
        await ws_client.run()


# 서비스 실행 헬퍼
async def run_balance_sync_service():
    """잔고 동기화 서비스 실행"""
    service = BalanceSyncService()
    await service.start()


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 서비스 실행
    asyncio.run(run_balance_sync_service())
