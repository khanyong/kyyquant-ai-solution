# 고급 거래 기능 백엔드 구현 계획

## 1. 프론트엔드 분석 결과

### 1.1 StrategyBuilder.tsx에서 저장하는 데이터 구조

```typescript
interface Strategy {
  // 기본 정보
  name: string
  description: string

  // 단계별 전략 (복합전략 A, B)
  useStageBasedStrategy?: boolean
  buyStageStrategy?: {
    stages: Array<{
      stage: number
      indicators: Array<{ /* 지표 조건 */ }>
      conditions: Array<{ /* 매수 조건 */ }>
      percentage: number  // 자본 할당 비율 (20%, 30%, 100%)
    }>
  }
  sellStageStrategy?: {
    stages: Array<{ /* 매도 단계 */ }>
  }

  // 목표 수익률 설정
  targetProfit?: {
    mode: 'simple' | 'staged'
    simple?: {
      enabled: boolean
      value: number  // 단순 목표 수익률 %
      combineWith: 'AND' | 'OR'
    }
    staged?: {
      enabled: boolean
      stages: Array<{
        stage: number
        targetProfit: number  // 단계별 목표 수익률
        exitRatio: number     // 해당 단계에서 매도 비율
        dynamicStopLoss?: boolean
      }>
    }
  }

  // 손절 설정
  stopLoss?: {
    enabled: boolean
    value: number  // 손실률 %
    breakEven?: boolean  // 본전 손절
    trailingStop?: {
      enabled: boolean
      activation: number  // 활성화 수익률
      distance: number    // 최고점 대비 하락률
    }
  }

  // 리스크 관리
  riskManagement: {
    stopLoss: number      // 구버전 호환
    takeProfit: number    // 구버전 호환
    trailingStop: boolean
    trailingStopPercent: number
    positionSize: number
    maxPositions: number
    systemCut?: boolean   // 시스템 CUT
  }

  // 고급 옵션
  advanced?: {
    splitTrading?: {
      enabled: boolean
      levels: number
      percentages: number[]  // [40, 30, 30] 형태
    }
    pyramiding?: {
      enabled: boolean
      maxLevels: number
    }
  }
}
```

### 1.2 TradingSettings.tsx의 분할매매 설정

```typescript
interface SplitTrading {
  enabled: boolean
  buyLevels: Array<{
    level: number      // 1차, 2차, 3차
    percentage: number // 비중 %
    trigger: number    // 트리거 가격 (현재가 대비 %)
  }>
  sellLevels: Array<{
    level: number
    percentage: number
    trigger: number    // 수익률 트리거 %
  }>
}
```

## 2. 백엔드 구현 요구사항

### 2.1 필수 구현 기능

1. **단계별 전략 실행 (Stage-based Strategy)**
   - 1단계 충족 시: 자본금의 20% 매수
   - 2단계 충족 시: 잔여 자본금의 30% 추가 매수
   - 3단계 충족 시: 잔여 자본금 100% 전량 매수
   - 각 단계별 독립적인 지표/조건 평가

2. **분할매매 시스템 (Split Trading)**
   - 분할 매수: 가격 하락 시 단계별 추가 매수
   - 분할 매도: 목표 수익률 도달 시 단계별 부분 매도
   - 각 단계별 비중과 트리거 가격 관리

3. **목표 수익률 관리 (Target Profit)**
   - 단순 모드: 특정 수익률 도달 시 전량 매도
   - 단계별 모드: 각 수익률 구간별 부분 매도
   - 동적 손절 연동 옵션

4. **손절 시스템 (Stop Loss)**
   - 기본 손절: 특정 손실률 도달 시 매도
   - 본전 손절: 수익 후 본전 회귀 시 매도
   - 트레일링 스탑: 최고점 대비 특정 % 하락 시 매도

5. **리스크 관리 (Risk Management)**
   - 포지션 사이즈 제한
   - 최대 보유 종목 수 제한
   - 시스템 CUT (연속 손실, 일일 최대 손실)

## 3. 구현 아키텍처

### 3.1 모듈 구조

```
backend/kiwoom_bridge/
├── core/
│   ├── position_manager.py      # 포지션 관리
│   ├── stage_executor.py        # 단계별 전략 실행
│   ├── split_trader.py          # 분할매매 처리
│   ├── risk_controller.py       # 리스크 관리
│   └── profit_target_manager.py # 목표 수익률 관리
├── strategy_engine.py            # 메인 전략 엔진 (수정)
├── backtest_engine_advanced.py  # 백테스트 엔진 (수정)
└── advanced_trading_features.py # 기존 코드 활용
```

### 3.2 핵심 클래스 설계

```python
# core/position_manager.py
class PositionManager:
    """포지션 상태 및 이력 관리"""
    def __init__(self):
        self.positions = {}  # {stock_code: Position}
        self.stage_history = {}  # 단계별 매수 이력

    def add_position(self, stock_code, price, quantity, stage=None):
        """신규/추가 포지션 생성"""

    def update_position(self, stock_code, current_price):
        """포지션 가격 업데이트 및 수익률 계산"""

    def partial_exit(self, stock_code, ratio):
        """부분 매도 처리"""

# core/stage_executor.py
class StageExecutor:
    """단계별 전략 실행 엔진"""
    def __init__(self, strategy_config):
        self.use_stage_based = strategy_config.get('useStageBasedStrategy')
        self.buy_stages = strategy_config.get('buyStageStrategy', {})
        self.sell_stages = strategy_config.get('sellStageStrategy', {})
        self.capital_allocation = [0.2, 0.3, 1.0]  # 20%, 30%, 100%

    def evaluate_buy_stage(self, df, position):
        """현재 충족되는 매수 단계 평가"""
        if not self.use_stage_based:
            return None, 0

        current_stage = position.stage if position else 0

        for stage in self.buy_stages.get('stages', []):
            if stage['stage'] > current_stage:
                if self._evaluate_stage_conditions(df, stage):
                    return stage['stage'], self.capital_allocation[stage['stage']-1]

        return None, 0

# core/split_trader.py
class SplitTrader:
    """분할매매 처리"""
    def __init__(self, config):
        self.enabled = config.get('enabled', False)
        self.buy_levels = config.get('buyLevels', [])
        self.sell_levels = config.get('sellLevels', [])

    def check_split_buy(self, position, current_price):
        """분할 매수 신호 확인"""
        if not position:
            # 첫 매수
            return self.buy_levels[0]['percentage'] / 100

        # 추가 매수 체크
        price_change = ((current_price - position.entry_price) / position.entry_price) * 100

        for level in self.buy_levels:
            if price_change <= level['trigger'] and level['level'] > position.split_level:
                position.split_level = level['level']
                return level['percentage'] / 100

        return 0

    def check_split_sell(self, position):
        """분할 매도 신호 확인"""
        profit_pct = position.profit_pct

        for level in self.sell_levels:
            if profit_pct >= level['trigger']:
                if level['level'] not in position.sold_levels:
                    position.sold_levels.append(level['level'])
                    return level['percentage'] / 100

        return 0

# core/profit_target_manager.py
class ProfitTargetManager:
    """목표 수익률 관리"""
    def __init__(self, config):
        self.mode = config.get('mode', 'simple')
        self.simple_config = config.get('simple', {})
        self.staged_config = config.get('staged', {})

    def check_target_reached(self, position):
        """목표 수익률 도달 확인"""
        if self.mode == 'simple':
            if self.simple_config.get('enabled'):
                target = self.simple_config.get('value', 5)
                if position.profit_pct >= target:
                    return True, 1.0  # 전량 매도

        elif self.mode == 'staged':
            if self.staged_config.get('enabled'):
                for stage in self.staged_config.get('stages', []):
                    target = stage.get('targetProfit')
                    if position.profit_pct >= target:
                        if stage['stage'] not in position.profit_stages:
                            position.profit_stages.append(stage['stage'])
                            return True, stage.get('exitRatio', 0.3)

        return False, 0

# core/risk_controller.py
class RiskController:
    """리스크 관리 통합"""
    def __init__(self, config):
        self.stop_loss_config = config.get('stopLoss', {})
        self.trailing_stop_config = self.stop_loss_config.get('trailingStop', {})
        self.system_cut_enabled = config.get('riskManagement', {}).get('systemCut', False)

    def check_stop_loss(self, position):
        """손절 조건 확인"""
        if self.stop_loss_config.get('enabled'):
            stop_loss_value = self.stop_loss_config.get('value', -3)

            # 기본 손절
            if position.profit_pct <= stop_loss_value:
                return True, 1.0

            # 트레일링 스탑
            if self.trailing_stop_config.get('enabled'):
                activation = self.trailing_stop_config.get('activation', 5)
                distance = self.trailing_stop_config.get('distance', 2)

                if position.max_profit >= activation:
                    drop_from_peak = position.max_profit - position.profit_pct
                    if drop_from_peak >= distance:
                        return True, 1.0

        return False, 0
```

## 4. 통합 구현 플로우

### 4.1 매수 프로세스

```python
def process_buy_signal(df, position, strategy_config, available_capital):
    """통합 매수 신호 처리"""

    # 1. 단계별 전략 확인
    stage_executor = StageExecutor(strategy_config)
    stage, stage_ratio = stage_executor.evaluate_buy_stage(df, position)

    if stage:
        # 단계별 자본 할당
        buy_amount = available_capital * stage_ratio
        return {
            'action': 'buy',
            'amount': buy_amount,
            'stage': stage,
            'reason': f'Stage {stage} buy signal'
        }

    # 2. 분할매수 확인
    if strategy_config.get('advanced', {}).get('splitTrading', {}).get('enabled'):
        split_trader = SplitTrader(strategy_config['advanced']['splitTrading'])
        split_ratio = split_trader.check_split_buy(position, df['close'].iloc[-1])

        if split_ratio > 0:
            buy_amount = available_capital * split_ratio
            return {
                'action': 'buy',
                'amount': buy_amount,
                'reason': 'Split buy signal'
            }

    # 3. 일반 매수 신호
    # 기존 로직...
```

### 4.2 매도 프로세스

```python
def process_sell_signal(df, position, strategy_config):
    """통합 매도 신호 처리"""

    # 1. 리스크 관리 (손절) 우선
    risk_controller = RiskController(strategy_config)
    stop_loss, sl_ratio = risk_controller.check_stop_loss(position)

    if stop_loss:
        return {
            'action': 'sell',
            'ratio': sl_ratio,
            'reason': 'Stop loss triggered'
        }

    # 2. 목표 수익률 확인
    profit_manager = ProfitTargetManager(strategy_config.get('targetProfit', {}))
    target_reached, tp_ratio = profit_manager.check_target_reached(position)

    if target_reached:
        return {
            'action': 'sell',
            'ratio': tp_ratio,
            'reason': 'Target profit reached'
        }

    # 3. 분할매도 확인
    if strategy_config.get('advanced', {}).get('splitTrading', {}).get('enabled'):
        split_trader = SplitTrader(strategy_config['advanced']['splitTrading'])
        split_ratio = split_trader.check_split_sell(position)

        if split_ratio > 0:
            return {
                'action': 'sell',
                'ratio': split_ratio,
                'reason': 'Split sell signal'
            }

    # 4. 일반 매도 신호
    # 기존 로직...
```

## 5. 백테스트 엔진 수정

### 5.1 backtest_engine_advanced.py 수정 사항

```python
class AdvancedBacktestEngine:
    def __init__(self):
        self.position_manager = PositionManager()
        self.stage_executor = None
        self.split_trader = None
        self.profit_manager = None
        self.risk_controller = None

    def initialize_managers(self, strategy_config):
        """고급 기능 매니저 초기화"""
        self.stage_executor = StageExecutor(strategy_config)
        self.split_trader = SplitTrader(
            strategy_config.get('advanced', {}).get('splitTrading', {})
        )
        self.profit_manager = ProfitTargetManager(
            strategy_config.get('targetProfit', {})
        )
        self.risk_controller = RiskController(strategy_config)

    def run_backtest(self, df, strategy_config):
        """백테스트 실행"""
        self.initialize_managers(strategy_config)

        for i in range(len(df)):
            current_data = df.iloc[:i+1]

            # 포지션 업데이트
            for stock_code, position in self.position_manager.positions.items():
                position.update_price(current_data['close'].iloc[-1])

                # 매도 신호 처리
                sell_signal = self.process_sell_signal(
                    current_data, position, strategy_config
                )

                if sell_signal['action'] == 'sell':
                    self.execute_sell(position, sell_signal['ratio'])

            # 매수 신호 처리
            buy_signal = self.process_buy_signal(
                current_data,
                self.position_manager.positions.get(stock_code),
                strategy_config,
                self.available_capital
            )

            if buy_signal['action'] == 'buy':
                self.execute_buy(stock_code, buy_signal['amount'])
```

## 6. 구현 우선순위

### Phase 1 (핵심 기능)
1. PositionManager 구현
2. StageExecutor 구현 (복합전략 A, B 지원)
3. 백테스트 엔진 통합

### Phase 2 (리스크 관리)
1. RiskController 구현 (손절, 트레일링 스탑)
2. ProfitTargetManager 구현 (목표 수익률)
3. 실시간 거래 연동

### Phase 3 (고급 기능)
1. SplitTrader 구현 (분할매매)
2. 피라미딩 지원
3. 시스템 CUT 구현

## 7. 테스트 계획

### 7.1 단위 테스트
- 각 매니저 클래스별 독립 테스트
- 신호 생성 정확도 검증
- 자본 할당 계산 검증

### 7.2 통합 테스트
- 복합전략 A, B 실행 테스트
- 분할매매 시나리오 테스트
- 리스크 관리 동작 검증

### 7.3 성능 테스트
- 대용량 데이터 처리 성능
- 실시간 거래 응답 속도
- 메모리 사용량 최적화

## 8. 예상 일정

- **Week 1**: Phase 1 구현 (핵심 기능)
- **Week 2**: Phase 2 구현 (리스크 관리)
- **Week 3**: Phase 3 구현 (고급 기능)
- **Week 4**: 테스트 및 최적화

## 9. 주의사항

1. **데이터 일관성**: 프론트엔드와 백엔드 간 데이터 구조 완벽 동기화
2. **하위 호환성**: 기존 전략들이 정상 동작하도록 보장
3. **성능 최적화**: 실시간 거래에 영향 없도록 효율적 구현
4. **에러 처리**: 각 단계별 명확한 에러 로깅 및 처리
5. **설정 검증**: 잘못된 설정값에 대한 방어 코드 필수