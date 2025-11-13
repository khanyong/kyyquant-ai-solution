# 워크플로우 B v5 - 간소화 버전

## 📋 문제점

호가 조회(`kw_price_orderbook` 테이블)에 데이터가 없어서 워크플로우가 실패합니다.

## ✅ 해결 방안

**임시 해결책**: 호가 대신 현재가를 사용

현재 `kw_price_orderbook` 테이블에 데이터가 없으므로, 당분간 현재가를 매수/매도 호가로 사용합니다.

### 수정된 데이터 병합 로직

```javascript
// ✅ 호가 없이 현재가만 사용
sell_price: priceInfo.current_price,  // 현재가를 매도 호가로
buy_price: priceInfo.current_price,   // 현재가를 매수 호가로
```

이렇게 하면:
- **order_price가 0이 되는 문제는 해결됨**
- 실제 호가보다는 덜 정확하지만, 현재가를 기준으로 주문 가격 계산 가능
- offset을 적용하여 현재가보다 약간 높거나 낮은 가격으로 주문

### 주문 가격 계산 예시

```
현재가: 71,150원
offset: +10원

매수 주문 전략 (best_ask + offset):
  기준: 71,150 (현재가)
  offset: +10
  주문가: 71,160원

매도 주문 전략 (best_bid + offset):
  기준: 71,150 (현재가)
  offset: -10
  주문가: 71,140원
```

## 🔮 향후 개선 방안

### 1. 호가 데이터 수집 시스템 구축

별도 워크플로우를 만들어 키움 API에서 실시간 호가 정보를 가져와 `kw_price_orderbook` 테이블에 저장:

```javascript
// 키움 API: 실시간 호가 조회
GET /uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn
```

### 2. 현재가 기반 호가 추정

정확한 호가가 없을 때 현재가를 기준으로 호가를 추정:

```javascript
// Tick 단위를 고려한 호가 추정
function estimateAskBid(currentPrice) {
  const tickSize = getTickSize(currentPrice);
  return {
    ask: currentPrice + tickSize,
    bid: currentPrice - tickSize
  };
}

function getTickSize(price) {
  if (price < 1000) return 1;
  if (price < 5000) return 5;
  if (price < 10000) return 10;
  if (price < 50000) return 50;
  return 100;
}
```

### 3. WebSocket 실시간 호가 구독

n8n에서 WebSocket을 사용하여 키움 API의 실시간 호가 스트림을 구독:

```
WebSocket → kw_price_orderbook 테이블 실시간 업데이트
```

## 📝 현재 워크플로우 동작 방식

1. ✅ 전략 조회
2. ✅ 유니버스 종목 추출
3. ✅ 현재가 조회
4. ⚠️ ~~호가 조회~~ (스킵 - 데이터 없음)
5. ✅ 데이터 병합 (현재가만 사용)
6. ✅ 신호 생성
7. ✅ 주문 가격 계산 (현재가 기준 + offset)
8. ✅ 주문 실행

## 🎯 결과

- order_price: **0원 → 정상 가격** ✅
- 정확도: **호가 기준 → 현재가 기준** (약간 감소하지만 실용적)
- 안정성: **에러 없이 실행** ✅
