"""
백테스트 데이터 모델
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class BacktestRequest(BaseModel):
    """백테스트 요청 모델"""
    strategy_id: str
    start_date: str
    end_date: str
    initial_capital: float = 10000000
    commission: float = 0.00015
    slippage: float = 0.001
    data_interval: str = "1d"
    stock_codes: Optional[List[str]] = None
    filter_id: Optional[str] = None
    filter_rules: Optional[Dict[str, Any]] = None
    filtering_mode: Optional[str] = None

class Position(BaseModel):
    """포지션 모델"""
    stock_code: str
    stock_name: Optional[str] = None
    quantity: int
    avg_price: float
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_rate: Optional[float] = None
    entry_date: datetime
    entry_reason: str

class Trade(BaseModel):
    """거래 기록 모델"""
    trade_id: str
    stock_code: str
    stock_name: Optional[str] = None
    trade_type: str  # 'buy' or 'sell'
    quantity: int
    price: float
    total_amount: float
    commission: float
    timestamp: datetime
    reason: str
    stage: Optional[int] = None
    profit_loss: Optional[float] = None

class BacktestResult(BaseModel):
    """백테스트 결과 모델"""
    backtest_id: str
    strategy_id: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_rate: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    positions: List[Position] = []
    trades: List[Trade] = []
    daily_returns: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None