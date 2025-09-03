# 키움 OpenAPI 데이터 저장 요구사항

## 📊 필요한 테이블 및 컬럼 구조

### 1. **market_data** - 실시간 시장 데이터
키움 OpenAPI에서 제공하는 모든 실시간 데이터 저장

#### 필수 컬럼:
- `stock_code` - 종목코드
- `current_price` - 현재가
- `volume` - 거래량
- `change_rate` - 등락률
- `bid/ask_price` - 매수/매도 호가
- `timestamp` - 시간

#### 키움 API 매핑:
```python
# OnReceiveRealData 이벤트에서 수집
현재가 = GetCommRealData(종목코드, 10)
거래량 = GetCommRealData(종목코드, 15)
등락률 = GetCommRealData(종목코드, 12)
```

### 2. **technical_indicators** - 기술적 지표
전략 실행에 필요한 계산된 지표들

#### 필수 지표:
- **이동평균선**: MA5, MA10, MA20, MA60, MA120
- **RSI**: 과매수/과매도 신호
- **MACD**: 추세 전환 신호
- **볼린저밴드**: 변동성 분석
- **거래량 지표**: OBV, VWAP

### 3. **trading_signals** - 거래 신호 (개선)
#### 추가 필요 컬럼:
- `signal_strength` - 신호 강도 (weak/medium/strong)
- `confidence_score` - 신뢰도 점수 (0~1)
- `entry_price` - 진입 가격
- `target_price` - 목표 가격
- `stop_loss_price` - 손절 가격
- `indicators_snapshot` - 신호 생성 시점 지표 스냅샷

### 4. **kiwoom_orders** - 키움 주문 관리
#### 필수 컬럼:
- `kiwoom_order_no` - 키움 주문번호
- `account_no` - 계좌번호
- `order_status` - 주문상태 (접수/체결/취소)
- `executed_quantity` - 체결수량
- `executed_price` - 체결가격
- `commission` - 수수료
- `tax` - 세금

### 5. **positions** - 포지션 관리
#### 필수 컬럼:
- `quantity` - 보유수량
- `available_quantity` - 매도가능수량
- `avg_buy_price` - 평균매입가
- `profit_loss` - 평가손익
- `stop_loss_price` - 손절가
- `take_profit_price` - 익절가

### 6. **account_balance** - 계좌 잔고
#### 필수 컬럼:
- `total_evaluation` - 총평가금액
- `available_cash` - 주문가능금액
- `total_profit_loss` - 총평가손익
- `total_profit_loss_rate` - 총수익률

## 🔄 데이터 흐름

```
키움 OpenAPI
    ↓
1. 실시간 데이터 수집 (OnReceiveRealData)
    → market_data 테이블
    
2. 기술적 지표 계산
    → technical_indicators 테이블
    
3. 전략 조건 확인
    → trading_signals 테이블
    
4. 주문 실행 (SendOrder)
    → kiwoom_orders 테이블
    
5. 체결 확인 (OnReceiveChejanData)
    → positions 테이블 업데이트
    
6. 잔고 조회 (계좌평가잔고내역요청)
    → account_balance 테이블
```

## 📝 SQL 마이그레이션 적용 방법

1. Supabase SQL Editor에서 실행:
```sql
-- 1단계: 기본 테이블 생성
supabase/migrations/complete_trading_schema.sql 실행

-- 2단계: 기존 테이블 수정
ALTER TABLE 문 실행

-- 3단계: 인덱스 생성
CREATE INDEX 문 실행

-- 4단계: RLS 정책 적용
CREATE POLICY 문 실행
```

## ⚠️ 주의사항

1. **데이터 저장 주기**
   - 실시간 데이터: 체결 시마다
   - 기술적 지표: 1분/5분 단위
   - 계좌 잔고: 5분 단위

2. **데이터 보관 기간**
   - 실시간 데이터: 30일
   - 지표 데이터: 90일
   - 거래 기록: 영구 보관

3. **성능 최적화**
   - 인덱스 활용
   - 배치 삽입
   - 오래된 데이터 아카이빙