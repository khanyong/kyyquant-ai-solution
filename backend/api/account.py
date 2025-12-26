"""
키움증권 계좌 관리 API
계좌 정보, 잔고, 거래 내역 조회
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from .kiwoom_client import get_kiwoom_client

router = APIRouter()


class AccountInfoResponse(BaseModel):
    """계좌 정보 응답"""
    account_no: str
    is_demo: bool
    total_asset: float = 0  # 총 자산
    cash_balance: float = 0  # 예수금
    stock_value: float = 0  # 주식 평가 금액
    profit_loss: float = 0  # 평가 손익
    profit_loss_rate: float = 0  # 수익률 (%)
    timestamp: datetime


class StockHoldingResponse(BaseModel):
    """보유 종목 정보"""
    stock_code: str
    stock_name: str
    quantity: int
    available_quantity: int  # 매도 가능 수량
    average_price: float  # 평균 매입가
    current_price: float
    profit_loss: float
    profit_loss_rate: float
    value: float  # 평가 금액


class BalanceResponse(BaseModel):
    """잔고 조회 응답"""
    account_no: str
    total_asset: float
    cash_balance: float
    stock_value: float
    holdings: List[StockHoldingResponse]
    timestamp: datetime


@router.get("/info", response_model=AccountInfoResponse)
async def get_account_info():
    """
    계좌 정보 조회

    Returns:
        AccountInfoResponse: 계좌 기본 정보
    """
    try:
        kiwoom_client = get_kiwoom_client()

        # 계좌 잔고 조회
        balance_data = kiwoom_client.get_account_balance()

        if not balance_data:
            raise HTTPException(
                status_code=503,
                detail="계좌 정보 조회 실패 - 키움 API 연결을 확인하세요"
            )

        summary = balance_data.get('summary', {})
        
        return AccountInfoResponse(
            account_no=balance_data['account_no'],
            is_demo=kiwoom_client.is_demo,
            total_asset=summary.get('total_assets', 0),
            cash_balance=summary.get('withdrawable_amount', 0),
            stock_value=summary.get('total_evaluation_amount', 0),
            profit_loss=summary.get('total_evaluation_profit_loss', 0),
            profit_loss_rate=summary.get('total_earning_rate', 0),
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계좌 정보 조회 오류: {str(e)}")


@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """
    잔고 조회 (보유 종목 포함)

    Returns:
        BalanceResponse: 계좌 잔고 및 보유 종목
    """
    try:
        kiwoom_client = get_kiwoom_client()

        # 계좌 잔고 조회
        balance_data = kiwoom_client.get_account_balance()
        if not balance_data:
            raise HTTPException(
                status_code=503,
                detail="계좌 잔고 조회 실패"
            )

        # 보유 종목 조회
        holdings_data = balance_data.get('holdings', [])

        # 보유 종목 변환
        holdings = []
        for holding in holdings_data:
            # Pydantic 모델에 필요한 필드 보완
            if 'available_quantity' not in holding:
                holding['available_quantity'] = holding.get('quantity', 0)
            if 'value' not in holding:
                holding['value'] = holding.get('current_price', 0) * holding.get('quantity', 0)
            
            holdings.append(StockHoldingResponse(**holding))

        summary = balance_data.get('summary', {})

        # [AUTO-SYNC] Update DB with latest balance
        try:
             # Lazy import to avoid circular dependency issues if any,
             # though provider.py checks config. Here we use raw supabase-py or env vars?
             # backend typically has a singleton supabase client available.
             # Checking `backend/data/provider.py` or similar for standard client access is better.
             # But for now, using the pattern from `kiwoom_client` fetching secrets is okay?
             # Actually, best to use os.getenv and create client locally or reuse one if available.
             # Given this is fastapi app, let's look for a `deps.py` or similar later.
             # For now, inline creation is safe for low-frequency calls.
             import os
             from supabase import create_client
             
             sb_url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
             sb_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
             
             if sb_url and sb_key:
                 supabase = create_client(sb_url, sb_key)
                 
                 # 1. Update Account Balance Table
                 # Need user_id. Quickest way is from strategies table or user_api_keys.
                 # Assuming single user system for now as per scripts.
                 user_res = supabase.table('strategies').select('user_id').limit(1).execute()
                 if user_res.data:
                     user_id = user_res.data[0]['user_id']
                     
                     total_asset = float(summary.get('total_assets', 0))
                     if total_asset == 0: total_asset = float(summary.get('deposit', 0))
                     
                     supabase.table('kw_account_balance').upsert({
                        'user_id': user_id,
                        'account_number': balance_data['account_no'],
                        'total_asset': int(total_asset),
                        'available_cash': int(summary.get('withdrawable_amount', 0)),
                        'deposit': int(float(summary.get('deposit', 0))),
                        'updated_at': datetime.now().isoformat()
                     }).execute()
                     
                     # 2. Update Strategy Allocation (The "System Logic")
                     # Only if Total Asset is valid (>0)
                     if total_asset > 0:
                         target_alloc = int(total_asset * 0.5)
                         strategies = ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']
                         
                         supabase.table('strategies').update({
                            'allocated_capital': target_alloc,
                            'allocated_percent': 0.5
                         }).in_('name', strategies).execute()
                         
        except Exception as sync_e:
            print(f"[AutoStock] Balance Sync Failed: {sync_e}")
            # Do not fail the API response just because DB sync failed
            pass

        return BalanceResponse(
            account_no=balance_data['account_no'],
            total_asset=summary.get('total_assets', 0),
            cash_balance=summary.get('withdrawable_amount', 0),
            stock_value=summary.get('total_evaluation_amount', 0),
            holdings=holdings,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"잔고 조회 오류: {str(e)}")


@router.get("/holdings", response_model=List[StockHoldingResponse])
async def get_holdings():
    """
    보유 종목 조회

    Returns:
        List[StockHoldingResponse]: 보유 종목 리스트
    """
    try:
        kiwoom_client = get_kiwoom_client()

        balance_data = kiwoom_client.get_account_balance()
        holdings_data = balance_data.get('holdings', []) if balance_data else []
        if holdings_data is None:
            return []

        return [
            StockHoldingResponse(**holding)
            for holding in holdings_data
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보유 종목 조회 오류: {str(e)}")


@router.get("/status")
async def get_account_status():
    """
    계좌 연결 상태 확인

    Returns:
        계좌 API 연결 상태
    """
    try:
        kiwoom_client = get_kiwoom_client()

        return {
            "status": "connected",
            "account_no": kiwoom_client.account_no,
            "has_credentials": bool(kiwoom_client.app_key and kiwoom_client.app_secret),
            "is_demo": kiwoom_client.is_demo,
            "mode": "모의투자" if kiwoom_client.is_demo else "실전투자",
            "api_url": kiwoom_client.base_url,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계좌 상태 확인 오류: {str(e)}")
