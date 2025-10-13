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

        return AccountInfoResponse(
            account_no=balance_data['account_no'],
            is_demo=kiwoom_client.is_demo,
            total_asset=balance_data['total_asset'],
            cash_balance=balance_data['cash_balance'],
            stock_value=balance_data['stock_value'],
            profit_loss=balance_data['profit_loss'],
            profit_loss_rate=balance_data['profit_loss_rate'],
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
        holdings_data = kiwoom_client.get_holdings()
        if holdings_data is None:
            holdings_data = []

        # 보유 종목 변환
        holdings = [
            StockHoldingResponse(**holding)
            for holding in holdings_data
        ]

        return BalanceResponse(
            account_no=balance_data['account_no'],
            total_asset=balance_data['total_asset'],
            cash_balance=balance_data['cash_balance'],
            stock_value=balance_data['stock_value'],
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

        holdings_data = kiwoom_client.get_holdings()
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
