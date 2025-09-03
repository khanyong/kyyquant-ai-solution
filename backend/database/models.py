"""
Pydantic models for API request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# Request Models
class LoginRequest(BaseModel):
    account_no: Optional[str] = Field(None, description="계좌번호")
    password: Optional[str] = Field(None, description="비밀번호")
    demo_mode: bool = Field(True, description="모의투자 모드")


class OrderRequest(BaseModel):
    account_no: str = Field(..., description="계좌번호")
    stock_code: str = Field(..., description="종목코드")
    order_type: Literal["buy", "sell"] = Field(..., description="주문 타입")
    quantity: int = Field(..., gt=0, description="주문 수량")
    price: int = Field(..., ge=0, description="주문 가격")
    order_method: Literal["limit", "market"] = Field("limit", description="주문 방식")


class StockInfoRequest(BaseModel):
    stock_code: str = Field(..., description="종목코드")


class BalanceRequest(BaseModel):
    account_no: str = Field(..., description="계좌번호")


# Response Models
class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    accounts: List[str] = []
    server_type: str = "모의투자"


class StockInfo(BaseModel):
    code: str
    name: str
    price: int
    change: int
    changeRate: float
    volume: int
    high: Optional[int] = None
    low: Optional[int] = None
    open: Optional[int] = None


class Portfolio(BaseModel):
    stockCode: str
    stockName: str
    quantity: int
    avgPrice: int
    currentPrice: int
    profitLoss: int
    profitLossRate: float


class BalanceResponse(BaseModel):
    account_no: str
    holdings: List[Portfolio]
    total_value: Optional[int] = None
    total_profit_loss: Optional[int] = None
    timestamp: datetime


class OrderResponse(BaseModel):
    success: bool
    message: str
    order_no: Optional[str] = None
    order: Optional[OrderRequest] = None


class MarketStocksResponse(BaseModel):
    market: str
    count: int
    total: int
    stocks: List[StockInfo]


class HealthResponse(BaseModel):
    status: str
    kiwoom_api: str
    timestamp: datetime
    mode: Optional[str] = None


class WebSocketMessage(BaseModel):
    type: Literal["subscribe", "unsubscribe", "ping", "real_data", "subscribed", "unsubscribed", "pong", "error"]
    stock_code: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None


class RealTimeData(BaseModel):
    code: str
    time: datetime
    price: int
    change: int
    changeRate: float
    volume: int
    totalVolume: int