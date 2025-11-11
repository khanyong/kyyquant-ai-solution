-- strategies 테이블에 주문 가격 전략 컬럼 추가

ALTER TABLE strategies
ADD COLUMN IF NOT EXISTS order_price_strategy JSONB DEFAULT '{
  "buy": {
    "type": "best_ask",
    "offset": 0
  },
  "sell": {
    "type": "best_bid",
    "offset": 0
  }
}'::jsonb;

COMMENT ON COLUMN strategies.order_price_strategy IS '주문 가격 전략 설정

buy.type 옵션:
- "best_ask": 매도 1호가 (즉시 체결)
- "best_bid": 매수 1호가 (대기)
- "mid_price": 중간가 (매도1호가 + 매수1호가) / 2
- "market": 시장가 주문

sell.type 옵션:
- "best_bid": 매수 1호가 (즉시 체결)
- "best_ask": 매도 1호가 (대기)
- "mid_price": 중간가
- "market": 시장가 주문

offset: 가격 조정 (원 단위)
- 양수: 가격 올림 (매수 시 더 비싸게, 매도 시 더 비싸게)
- 음수: 가격 내림 (매수 시 더 싸게, 매도 시 더 싸게)
- 예: offset=10 → 매수 1호가 + 10원

예시:
{
  "buy": {
    "type": "best_ask",    // 매도 1호가로 매수 (즉시 체결)
    "offset": 10           // +10원 (체결 확률 UP)
  },
  "sell": {
    "type": "best_bid",    // 매수 1호가로 매도 (즉시 체결)
    "offset": -10          // -10원 (체결 확률 UP)
  }
}
';

-- 기존 데이터 업데이트 (기본값 설정)
UPDATE strategies
SET order_price_strategy = '{
  "buy": {
    "type": "best_ask",
    "offset": 10
  },
  "sell": {
    "type": "best_bid",
    "offset": -10
  }
}'::jsonb
WHERE order_price_strategy IS NULL;
