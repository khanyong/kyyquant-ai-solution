"""
전략 설정 스키마 - 모든 전략 요소들의 체계적 관리
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class SignalType(str, Enum):
    """신호 타입"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class OrderMethod(str, Enum):
    """주문 방식"""
    MARKET = "market"  # 시장가
    LIMIT = "limit"    # 지정가
    STOP = "stop"      # 스톱
    STOP_LIMIT = "stop_limit"  # 스톱 리밋

class IndicatorConfig(BaseModel):
    """기술적 지표 설정"""
    # 이동평균선
    sma_enabled: bool = Field(True, description="단순이동평균 사용")
    sma_periods: List[int] = Field([5, 20, 60, 120], description="SMA 기간")
    
    ema_enabled: bool = Field(False, description="지수이동평균 사용")
    ema_periods: List[int] = Field([12, 26], description="EMA 기간")
    
    # 모멘텀 지표
    rsi_enabled: bool = Field(True, description="RSI 사용")
    rsi_period: int = Field(14, description="RSI 기간")
    rsi_oversold: float = Field(30, description="과매도 기준")
    rsi_overbought: float = Field(70, description="과매수 기준")
    
    # MACD
    macd_enabled: bool = Field(True, description="MACD 사용")
    macd_fast: int = Field(12, description="MACD 단기")
    macd_slow: int = Field(26, description="MACD 장기")
    macd_signal: int = Field(9, description="MACD 시그널")
    
    # 볼린저 밴드
    bb_enabled: bool = Field(True, description="볼린저밴드 사용")
    bb_period: int = Field(20, description="볼린저밴드 기간")
    bb_std_dev: float = Field(2.0, description="표준편차 배수")
    
    # 거래량
    volume_enabled: bool = Field(True, description="거래량 분석 사용")
    volume_ma_period: int = Field(20, description="거래량 이평 기간")
    volume_ratio_threshold: float = Field(1.5, description="거래량 급증 기준")
    
    # Stochastic
    stoch_enabled: bool = Field(False, description="스토캐스틱 사용")
    stoch_k_period: int = Field(14, description="K 기간")
    stoch_d_period: int = Field(3, description="D 기간")
    stoch_oversold: float = Field(20, description="과매도 기준")
    stoch_overbought: float = Field(80, description="과매수 기준")

class EntryConditions(BaseModel):
    """진입 조건 설정"""
    # 기본 진입 조건
    use_trend_confirmation: bool = Field(True, description="추세 확인 필요")
    min_volume_ratio: float = Field(1.0, description="최소 거래량 비율")
    
    # 매수 진입
    buy_signals_required: int = Field(2, description="필요한 매수 신호 수")
    buy_rsi_max: float = Field(70, description="매수 시 최대 RSI")
    buy_position_from_bb: str = Field("lower", description="볼린저밴드 위치")
    
    # 매도 진입
    sell_signals_required: int = Field(1, description="필요한 매도 신호 수")
    sell_rsi_min: float = Field(30, description="매도 시 최소 RSI")
    
    # 추가 필터
    avoid_gap: bool = Field(True, description="갭 발생 시 회피")
    max_spread_percent: float = Field(0.5, description="최대 스프레드 %")
    time_filter_enabled: bool = Field(True, description="시간대 필터 사용")
    allowed_hours: List[int] = Field([9, 10, 11, 13, 14], description="거래 허용 시간")

class ExitConditions(BaseModel):
    """청산 조건 설정"""
    # 손절/익절
    stop_loss_enabled: bool = Field(True, description="손절 사용")
    stop_loss_percent: float = Field(5.0, description="손절 %")
    stop_loss_atr_multiplier: float = Field(2.0, description="ATR 기반 손절")
    
    take_profit_enabled: bool = Field(True, description="익절 사용")
    take_profit_percent: float = Field(10.0, description="익절 %")
    take_profit_atr_multiplier: float = Field(3.0, description="ATR 기반 익절")
    
    # Trailing Stop
    trailing_stop_enabled: bool = Field(False, description="추적 손절 사용")
    trailing_stop_percent: float = Field(3.0, description="추적 손절 %")
    trailing_stop_activation: float = Field(5.0, description="추적 손절 활성화 수익률")
    
    # 시간 기반 청산
    time_stop_enabled: bool = Field(False, description="시간 청산 사용")
    max_holding_days: int = Field(30, description="최대 보유 일수")
    
    # 시장 조건 청산
    exit_on_signal_reverse: bool = Field(True, description="신호 반전 시 청산")
    exit_on_volume_dry: bool = Field(False, description="거래량 감소 시 청산")

class RiskManagement(BaseModel):
    """리스크 관리 설정"""
    # 포지션 크기
    position_sizing_method: str = Field("fixed_percent", description="포지션 크기 방법")
    fixed_position_percent: float = Field(10.0, description="고정 포지션 비율")
    kelly_fraction: float = Field(0.25, description="켈리 공식 비율")
    
    # 리스크 제한
    max_position_size: float = Field(30.0, description="최대 포지션 크기 %")
    max_positions: int = Field(5, description="최대 보유 종목 수")
    max_sector_exposure: float = Field(40.0, description="섹터별 최대 노출 %")
    
    # 일일 제한
    daily_loss_limit: float = Field(3.0, description="일일 손실 한도 %")
    daily_trade_limit: int = Field(10, description="일일 거래 횟수 제한")
    
    # 상관관계
    correlation_check: bool = Field(True, description="상관관계 체크")
    max_correlation: float = Field(0.7, description="최대 허용 상관계수")
    
    # 변동성 필터
    volatility_filter: bool = Field(True, description="변동성 필터 사용")
    max_volatility: float = Field(0.05, description="최대 허용 변동성")
    min_volatility: float = Field(0.001, description="최소 필요 변동성")

class BacktestSettings(BaseModel):
    """백테스트 설정"""
    initial_capital: float = Field(10000000, description="초기 자본금")
    commission_rate: float = Field(0.00015, description="수수료율")
    slippage_rate: float = Field(0.001, description="슬리피지율")
    
    start_date: str = Field("2020-01-01", description="시작일")
    end_date: str = Field("2024-12-31", description="종료일")
    
    # 백테스트 옵션
    use_adjusted_close: bool = Field(True, description="수정 종가 사용")
    reinvest_profits: bool = Field(True, description="수익 재투자")
    consider_dividends: bool = Field(False, description="배당 고려")
    
    # 벤치마크
    benchmark_enabled: bool = Field(True, description="벤치마크 비교")
    benchmark_symbol: str = Field("KOSPI", description="벤치마크 심볼")

class NotificationSettings(BaseModel):
    """알림 설정"""
    # 알림 채널
    email_enabled: bool = Field(False, description="이메일 알림")
    email_address: str = Field("", description="이메일 주소")
    
    telegram_enabled: bool = Field(False, description="텔레그램 알림")
    telegram_chat_id: str = Field("", description="텔레그램 채팅 ID")
    
    discord_enabled: bool = Field(False, description="디스코드 알림")
    discord_webhook: str = Field("", description="디스코드 웹훅")
    
    # 알림 조건
    notify_on_entry: bool = Field(True, description="진입 시 알림")
    notify_on_exit: bool = Field(True, description="청산 시 알림")
    notify_on_stop_loss: bool = Field(True, description="손절 시 알림")
    notify_on_error: bool = Field(True, description="에러 시 알림")
    notify_daily_summary: bool = Field(True, description="일일 요약 알림")

class StrategyConfig(BaseModel):
    """전체 전략 설정"""
    # 기본 정보
    name: str = Field(..., description="전략 이름")
    version: str = Field("1.0.0", description="버전")
    description: str = Field("", description="전략 설명")
    author: str = Field("", description="작성자")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 전략 타입
    strategy_type: str = Field("momentum", description="전략 유형")
    timeframe: str = Field("1d", description="시간프레임")
    universe: List[str] = Field([], description="대상 종목 리스트")
    
    # 활성화 상태
    is_active: bool = Field(False, description="활성화 여부")
    is_test_mode: bool = Field(True, description="테스트 모드")
    auto_trade_enabled: bool = Field(False, description="자동매매 활성화")
    
    # 상세 설정
    indicators: IndicatorConfig = Field(default_factory=IndicatorConfig)
    entry_conditions: EntryConditions = Field(default_factory=EntryConditions)
    exit_conditions: ExitConditions = Field(default_factory=ExitConditions)
    risk_management: RiskManagement = Field(default_factory=RiskManagement)
    backtest_settings: BacktestSettings = Field(default_factory=BacktestSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    
    # 커스텀 파라미터 (전략별 특수 설정)
    custom_parameters: Dict[str, Any] = Field({}, description="커스텀 파라미터")
    
    # 성과 메트릭 (자동 업데이트)
    performance_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_return": 0,
            "sharpe_ratio": 0,
            "max_drawdown": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "total_trades": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "last_updated": None
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Advanced Momentum Strategy",
                "version": "2.0.0",
                "description": "모멘텀 기반 자동매매 전략",
                "strategy_type": "momentum",
                "timeframe": "1d",
                "universe": ["005930", "000660", "035720"],
                "indicators": {
                    "rsi_enabled": True,
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70
                },
                "risk_management": {
                    "max_position_size": 20,
                    "max_positions": 3,
                    "daily_loss_limit": 2
                }
            }
        }


def create_strategy_tables_sql():
    """향상된 전략 테이블 SQL"""
    return """
    -- 전략 마스터 테이블 (모든 설정 포함)
    CREATE TABLE IF NOT EXISTS strategies_v2 (
        id SERIAL PRIMARY KEY,
        
        -- 기본 정보
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        description TEXT,
        author TEXT,
        strategy_type TEXT NOT NULL,
        timeframe TEXT DEFAULT '1d',
        universe TEXT[], -- 대상 종목 배열
        
        -- 상태
        is_active BOOLEAN DEFAULT FALSE,
        is_test_mode BOOLEAN DEFAULT TRUE,
        auto_trade_enabled BOOLEAN DEFAULT FALSE,
        
        -- 전체 설정 (JSON)
        indicators JSONB NOT NULL,
        entry_conditions JSONB NOT NULL,
        exit_conditions JSONB NOT NULL,
        risk_management JSONB NOT NULL,
        backtest_settings JSONB,
        notifications JSONB,
        custom_parameters JSONB,
        
        -- 성과 메트릭
        performance_metrics JSONB,
        last_signal_at TIMESTAMPTZ,
        last_trade_at TIMESTAMPTZ,
        
        -- 코드 및 메타데이터
        strategy_code TEXT, -- Python 코드
        code_hash TEXT, -- 코드 버전 체크용
        
        -- 타임스탬프
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        
        -- 사용자
        user_id UUID REFERENCES auth.users(id),
        
        UNIQUE(name, version, user_id)
    );
    
    -- 전략 실행 로그 (상세)
    CREATE TABLE IF NOT EXISTS strategy_execution_logs (
        id SERIAL PRIMARY KEY,
        strategy_id INTEGER REFERENCES strategies_v2(id),
        
        execution_time TIMESTAMPTZ NOT NULL,
        market_data JSONB, -- 실행 시점의 시장 데이터
        
        -- 지표 값들
        indicator_values JSONB,
        
        -- 조건 체크 결과
        entry_conditions_met JSONB,
        exit_conditions_met JSONB,
        risk_checks_passed JSONB,
        
        -- 신호 및 결정
        signal_generated TEXT,
        signal_strength FLOAT,
        action_taken TEXT,
        action_reason TEXT,
        
        -- 주문 정보
        order_placed BOOLEAN DEFAULT FALSE,
        order_details JSONB,
        
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- 전략 최적화 결과
    CREATE TABLE IF NOT EXISTS strategy_optimizations (
        id SERIAL PRIMARY KEY,
        strategy_id INTEGER REFERENCES strategies_v2(id),
        
        optimization_date DATE NOT NULL,
        parameter_grid JSONB, -- 테스트한 파라미터 조합
        
        best_parameters JSONB,
        best_sharpe FLOAT,
        best_return FLOAT,
        
        all_results JSONB, -- 모든 조합의 결과
        
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- 인덱스
    CREATE INDEX idx_strategies_v2_active ON strategies_v2(is_active, user_id);
    CREATE INDEX idx_strategies_v2_type ON strategies_v2(strategy_type);
    CREATE INDEX idx_execution_logs_strategy ON strategy_execution_logs(strategy_id, execution_time);
    CREATE INDEX idx_execution_logs_signal ON strategy_execution_logs(signal_generated);
    
    -- 트리거: updated_at 자동 업데이트
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    CREATE TRIGGER update_strategies_v2_updated_at 
    BEFORE UPDATE ON strategies_v2 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """