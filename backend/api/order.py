"""
키움증권 주문 관리 API
매수, 매도, 주문 취소 기능
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .kiwoom_client import get_kiwoom_client

router = APIRouter()


class OrderRequest(BaseModel):
    """주문 요청"""
    stock_code: str = Field(..., description="종목코드", example="005930")
    quantity: int = Field(..., description="주문 수량", gt=0)
    price: int = Field(0, description="주문 가격 (0이면 시장가)", ge=0)
    order_type: str = Field(..., description="주문 유형 (buy/sell)", pattern="^(buy|sell)$")


class OrderResponse(BaseModel):
    """주문 응답"""
    order_no: str
    status: str  # success, error
    message: str
    stock_code: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    order_type: Optional[str] = None
    timestamp: datetime


@router.post("/buy", response_model=OrderResponse)
async def buy_stock(request: OrderRequest):
    """
    매수 주문

    Args:
        request: 주문 정보 (종목코드, 수량, 가격)

    Returns:
        OrderResponse: 주문 결과
    """
    try:
        kiwoom_client = get_kiwoom_client()

        # 매수 주문 실행
        result = kiwoom_client.order_stock(
            stock_code=request.stock_code,
            quantity=request.quantity,
            price=request.price,
            order_type="buy"
        )

        if not result:
            raise HTTPException(
                status_code=503,
                detail="주문 실행 실패 - 키움 API 연결을 확인하세요"
            )

        if result['status'] == 'error':
            raise HTTPException(
                status_code=400,
                detail=f"주문 실패: {result['message']}"
            )

        return OrderResponse(
            order_no=result.get('order_no', ''),
            status=result['status'],
            message=result['message'],
            stock_code=request.stock_code,
            quantity=request.quantity,
            price=request.price,
            order_type="buy",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매수 주문 오류: {str(e)}")


@router.post("/sell", response_model=OrderResponse)
async def sell_stock(request: OrderRequest):
    """
    매도 주문

    Args:
        request: 주문 정보 (종목코드, 수량, 가격)

    Returns:
        OrderResponse: 주문 결과
    """
    try:
        kiwoom_client = get_kiwoom_client()

        # 매도 주문 실행
        result = kiwoom_client.order_stock(
            stock_code=request.stock_code,
            quantity=request.quantity,
            price=request.price,
            order_type="sell"
        )

        if not result:
            raise HTTPException(
                status_code=503,
                detail="주문 실행 실패 - 키움 API 연결을 확인하세요"
            )

        if result['status'] == 'error':
            raise HTTPException(
                status_code=400,
                detail=f"주문 실패: {result['message']}"
            )

        return OrderResponse(
            order_no=result.get('order_no', ''),
            status=result['status'],
            message=result['message'],
            stock_code=request.stock_code,
            quantity=request.quantity,
            price=request.price,
            order_type="sell",
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매도 주문 오류: {str(e)}")


@router.post("/order", response_model=OrderResponse)
async def place_order(request: OrderRequest):
    """
    통합 주문 (매수/매도 자동 처리)

    Args:
        request: 주문 정보

    Returns:
        OrderResponse: 주문 결과
    """
    try:
        if request.order_type == "buy":
            return await buy_stock(request)
        elif request.order_type == "sell":
            return await sell_stock(request)
        else:
            raise HTTPException(
                status_code=400,
                detail="주문 유형은 'buy' 또는 'sell'이어야 합니다"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주문 오류: {str(e)}")


@router.post("/market-buy")
async def market_buy(stock_code: str, quantity: int):
    """
    시장가 매수

    Args:
        stock_code: 종목코드
        quantity: 수량

    Returns:
        주문 결과
    """
    request = OrderRequest(
        stock_code=stock_code,
        quantity=quantity,
        price=0,
        order_type="buy"
    )
    return await buy_stock(request)


@router.post("/market-sell")
async def market_sell(stock_code: str, quantity: int):
    """
    시장가 매도

    Args:
        stock_code: 종목코드
        quantity: 수량

    Returns:
        주문 결과
    """
    request = OrderRequest(
        stock_code=stock_code,
        quantity=quantity,
        price=0,
        order_type="sell"
    )
    return await sell_stock(request)


class CancelOrderRequest(BaseModel):
    """주문 취소 요청"""
    stock_code: str = Field(..., description="종목코드")
    order_no: str = Field(..., description="원 주문번호")
    quantity: int = Field(0, description="취소 수량 (0이면 전량 취소)")


@router.post("/cancel")
async def cancel_order_endpoint(request: CancelOrderRequest):
    """
    주문 취소
    
    Args:
        request: 취소 요청 정보 (종목코드, 주문번호, 수량)
    
    Returns:
        취소 결과
    """
    try:
        kiwoom_client = get_kiwoom_client()
        
        result = kiwoom_client.cancel_order(
            stock_code=request.stock_code,
            order_no=request.order_no,
            quantity=request.quantity
        )
        
        if not result or result['status'] == 'error':
             raise HTTPException(
                status_code=400, 
                detail=result['message'] if result else "취소 요청 실패"
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주문 취소 오류: {str(e)}")


@router.get("/test")
async def test_order_api():
    """
    주문 API 테스트 (실제 주문 없음)

    Returns:
        API 연결 상태
    """
    try:
        kiwoom_client = get_kiwoom_client()

        return {
            "status": "ok",
            "message": "주문 API 준비 완료",
            "account_no": kiwoom_client.account_no,
            "is_demo": kiwoom_client.is_demo,
            "api_url": kiwoom_client.base_url,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테스트 오류: {str(e)}")
