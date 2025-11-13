# 워크플로우 B v5 - Order Price 수정 사항

## 🐛 문제점

**order_price가 0으로 저장되는 원인:**

1. **잘못된 필드 매핑** (라인 120):
   ```javascript
   sell_price: priceInfo.high_52w || priceInfo.current_price,  // ❌ 52주 최고가
   buy_price: priceInfo.low_52w || priceInfo.current_price,    // ❌ 52주 최저가
   ```
   - 52주 최고가/최저가를 매도/매수 호가로 잘못 사용
   - `kw_price_current` 테이블에는 호가 정보가 없음

2. **호가 데이터 조회 없음**:
   - 호가 정보는 `kw_price_orderbook` 테이블에 별도 저장됨
   - 워크플로우에서 이 테이블을 조회하지 않음

## ✅ 해결 방안

### 1. 호가 데이터 조회 노드 추가

**노드 위치**: "현재가 조회" 노드 다음

**노드 설정**:
- **Type**: Supabase (HTTP Request)
- **Method**: GET
- **URL**: `={{$node['환경변수 설정'].item(0).json.SUPABASE_URL}}/rest/v1/kw_price_orderbook`
- **Query Parameters**:
  - `select`: `stock_code,ask_price1,bid_price1,ask_volume1,bid_volume1`
  - `stock_code`: `in.({{$('유니버스 종목 추출').all().map(item => item.json.stock_code).join(',')}})`

**Headers**:
- `apikey`: `={{$node['환경변수 설정'].item(0).json.SUPABASE_ANON_KEY}}`
- `Authorization`: `=Bearer {{$node['환경변수 설정'].item(0).json.SUPABASE_ANON_KEY}}`

### 2. 데이터 병합 노드 수정 (3개 입력)

**수정된 코드**:
```javascript
const strategyData = $('유니버스 종목 추출').all();
const priceData = $('현재가 조회').all();
const orderbookData = $('호가 조회').all();

console.log(`📥 전략: ${strategyData.length}, 현재가: ${priceData.length}, 호가: ${orderbookData.length}`);

const results = [];

// 현재가와 호가를 stock_code로 매핑
const priceMap = {};
const orderbookMap = {};

for (const item of priceData) {
  const price = item.json;
  if (price && price.stock_code) {
    priceMap[price.stock_code] = price;
  }
}

for (const item of orderbookData) {
  const orderbook = item.json;
  if (orderbook && orderbook.stock_code) {
    orderbookMap[orderbook.stock_code] = orderbook;
  }
}

console.log(`📊 현재가: ${Object.keys(priceMap).length}, 호가: ${Object.keys(orderbookMap).length}`);

for (const item of strategyData) {
  const strategy = item.json;
  const priceInfo = priceMap[strategy.stock_code];
  const orderbookInfo = orderbookMap[strategy.stock_code];

  if (!priceInfo || !priceInfo.current_price) {
    console.log(`⚠️ ${strategy.stock_code}: 현재가 없음`);
    continue;
  }

  // 호가가 없으면 현재가를 대체값으로 사용
  const askPrice = orderbookInfo?.ask_price1 || priceInfo.current_price;
  const bidPrice = orderbookInfo?.bid_price1 || priceInfo.current_price;

  results.push({
    json: {
      ...strategy,
      stock_name: priceInfo.stock_name || strategy.stock_code,
      current_price: priceInfo.current_price,
      change_rate: priceInfo.change_rate || 0,
      volume: priceInfo.volume || 0,
      // ✅ 올바른 호가 매핑
      sell_price: askPrice,      // 매도 1호가 (ask)
      buy_price: bidPrice,        // 매수 1호가 (bid)
      ask_volume: orderbookInfo?.ask_volume1 || 0,
      bid_volume: orderbookInfo?.bid_volume1 || 0,
      updated_at: priceInfo.updated_at
    }
  });
}

console.log(`✅ ${results.length}개 종목 병합 완료`);

if (results.length === 0) {
  return [{ json: { status: 'no_data', message: '데이터 없음' } }];
}

return results;
```

### 3. 주문 가격 계산 로직 개선

**현재 코드 (라인 140)**: 이미 정상 작동
```javascript
switch (strategy.type) {
  case 'best_ask':
    basePrice = signal.sell_price;  // ✅ 이제 올바른 매도 1호가
    break;
  case 'best_bid':
    basePrice = signal.buy_price;   // ✅ 이제 올바른 매수 1호가
    break;
  case 'mid_price':
    basePrice = signal.current_price;
    break;
  case 'market':
    basePrice = null;
    break;
}
```

## 📋 수정 체크리스트

- [ ] 1. "호가 조회" 노드 추가 (Supabase)
- [ ] 2. "데이터 병합" 노드 입력 3개로 변경
- [ ] 3. "데이터 병합" 노드 코드 교체
- [ ] 4. 노드 연결 순서 확인:
  ```
  환경변수 설정 → 전략 조회 → 유니버스 종목 추출
                                    ↓
                                현재가 조회
                                    ↓
                                호가 조회
                                    ↓
  유니버스 종목 추출 → 데이터 병합 (3개 입력)
  ```
- [ ] 5. 워크플로우 저장
- [ ] 6. 테스트 실행

## 🧪 테스트 방법

1. **"호가 조회" 노드 단독 실행**
   - 출력에 `ask_price1`, `bid_price1` 필드 확인
   - 정상적인 가격 데이터가 있는지 확인

2. **"데이터 병합" 노드까지 실행**
   - 출력의 `sell_price`, `buy_price` 값 확인
   - 52주 최고가/최저가가 아닌 실제 호가인지 확인

3. **"주문 가격 계산" 노드까지 실행**
   - `order_price`가 0이 아닌 정상 값인지 확인
   - 콘솔 로그에서 계산 과정 확인

4. **전체 워크플로우 실행**
   - orders 테이블에 저장된 `order_price` 확인
   - 0이 아닌 정상 가격이 저장되었는지 확인

## 💡 추가 개선 사항

### Fallback 로직
호가 데이터가 없는 경우를 대비한 Fallback:
- **1순위**: 실제 호가 (ask_price1, bid_price1)
- **2순위**: 현재가 (current_price)
- **3순위**: 0 (최후의 수단)

### 에러 처리
```javascript
if (!askPrice || !bidPrice) {
  console.warn(`⚠️ ${strategy.stock_code}: 호가 없음, 현재가 사용`);
}

if (!priceInfo.current_price) {
  console.error(`❌ ${strategy.stock_code}: 모든 가격 데이터 없음, 스킵`);
  continue;
}
```

---

## 🎯 예상 결과

수정 후:
```
[buy] 005930: 기준=71200, offset=10, 주문가=71210
[buy] 000660: 기준=89500, offset=10, 주문가=89510
```

수정 전 (잘못된 상태):
```
[buy] 005930: 기준=undefined, offset=10, 주문가=null → DB에 0 저장
```
