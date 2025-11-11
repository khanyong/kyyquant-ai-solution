# 워크플로우 B: 자동 매매 실행 v1

## 개요
- **실행 주기**: 5분마다
- **역할**: DB 데이터 기반 신호 생성 및 자동 주문
- **의존성**: 워크플로우 A가 저장한 kw_price_current 데이터 사용

## 노드 구성

### 1. Schedule Trigger
```json
{
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "minutes",
          "minutesInterval": 5
        }
      ]
    }
  },
  "name": "5분마다 실행",
  "type": "n8n-nodes-base.scheduleTrigger"
}
```

### 2. 환경변수 설정
```json
{
  "parameters": {
    "values": {
      "string": [
        {
          "name": "SUPABASE_URL",
          "value": "https://hznkyaomtrpzcayayayh.supabase.co"
        },
        {
          "name": "SUPABASE_ANON_KEY",
          "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
      ]
    }
  },
  "name": "환경변수 설정",
  "type": "n8n-nodes-base.set"
}
```

### 3. 활성 전략 + 유니버스 조회
```json
{
  "parameters": {
    "method": "GET",
    "url": "={{$node[\"환경변수 설정\"].json[\"SUPABASE_URL\"]}}/rest/v1/rpc/get_active_strategies_with_universe",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{$node[\"환경변수 설정\"].json[\"SUPABASE_ANON_KEY\"]}}"
        },
        {
          "name": "Authorization",
          "value": "={{\"Bearer \" + $node[\"환경변수 설정\"].json[\"SUPABASE_ANON_KEY\"]}}"
        }
      ]
    }
  },
  "name": "활성 전략 조회",
  "type": "n8n-nodes-base.httpRequest"
}
```

### 4. 유니버스 종목 리스트 추출
```javascript
// Code 노드
const strategies = $input.all();
const envVars = $('환경변수 설정').first().json;

// 모든 전략의 종목을 수집 (중복 제거하지 않음 - 전략별로 다른 조건)
const results = [];

for (const item of strategies) {
  const strategy = item.json;

  if (!strategy.filtered_stocks || !Array.isArray(strategy.filtered_stocks)) {
    continue;
  }

  // 각 종목에 대해 전략 정보 포함
  strategy.filtered_stocks.forEach(stockCode => {
    results.push({
      json: {
        stock_code: stockCode,
        strategy_id: strategy.strategy_id,
        strategy_name: strategy.strategy_name,
        entry_conditions: strategy.entry_conditions,
        exit_conditions: strategy.exit_conditions,
        order_price_strategy: strategy.order_price_strategy || {
          buy: { type: 'best_ask', offset: 10 },
          sell: { type: 'best_bid', offset: -10 }
        },
        allocated_capital: strategy.allocated_capital,
        SUPABASE_URL: envVars.SUPABASE_URL,
        SUPABASE_ANON_KEY: envVars.SUPABASE_ANON_KEY
      }
    });
  });
}

console.log(`📊 총 ${results.length}개 종목×전략 조합 처리`);
return results;
```

### 5. 현재가 조회 (DB에서)
```json
{
  "parameters": {
    "method": "GET",
    "url": "={{$json.SUPABASE_URL}}/rest/v1/kw_price_current?stock_code=eq.{{$json.stock_code}}&select=*",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{$json.SUPABASE_ANON_KEY}}"
        },
        {
          "name": "Authorization",
          "value": "={{\"Bearer \" + $json.SUPABASE_ANON_KEY}}"
        }
      ]
    }
  },
  "name": "현재가 조회",
  "type": "n8n-nodes-base.httpRequest"
}
```

### 6. 데이터 병합
```javascript
// Code 노드
const strategyData = $('유니버스 종목 추출').all();
const priceData = $input.all();

const results = [];

for (let i = 0; i < strategyData.length; i++) {
  const strategy = strategyData[i].json;
  const price = priceData[i]?.json;

  if (!price || !Array.isArray(price) || price.length === 0) {
    console.log(`⚠️ ${strategy.stock_code}: 현재가 없음 (워크플로우 A 대기 중)`);
    continue;
  }

  const priceInfo = price[0];

  results.push({
    json: {
      ...strategy,
      current_price: priceInfo.current_price,
      change_rate: priceInfo.change_rate,
      volume: priceInfo.volume,
      sell_price: priceInfo.high_52w,  // 매도 1호가
      buy_price: priceInfo.low_52w,    // 매수 1호가
      updated_at: priceInfo.updated_at
    }
  });
}

console.log(`✅ ${results.length}개 종목 데이터 병합 완료`);
return results;
```

### 7. 매수/매도 신호 생성
```javascript
// Code 노드
const items = $input.all();
const signals = [];

for (const item of items) {
  const data = item.json;

  // 매수 조건 확인
  const buyConditions = data.entry_conditions?.buy || [];
  let buySignal = false;

  // TODO: 실제 지표 기반 조건 확인 (현재는 간단한 예시)
  // 실제로는 RSI, MACD 등 계산 필요
  if (buyConditions.length > 0) {
    // 예: 3% 이상 하락 시 매수
    if (data.change_rate < -3) {
      buySignal = true;
    }
  }

  // 매도 조건 확인 (보유 종목만)
  // TODO: positions 테이블 조회하여 실제 보유 여부 확인
  const sellConditions = data.exit_conditions?.sell || [];
  let sellSignal = false;

  if (sellConditions.length > 0) {
    // 예: 5% 이상 상승 시 매도
    if (data.change_rate > 5) {
      sellSignal = true;
    }
  }

  // 신호 생성
  if (buySignal) {
    signals.push({
      json: {
        signal_type: 'buy',
        ...data
      }
    });
  }

  if (sellSignal) {
    signals.push({
      json: {
        signal_type: 'sell',
        ...data
      }
    });
  }
}

console.log(`📊 ${signals.length}개 매매 신호 생성`);
return signals;
```

### 8. 주문 가격 계산
```javascript
// Code 노드
const items = $input.all();
const results = [];

for (const item of items) {
  const signal = item.json;

  // 주문 가격 전략
  const strategy = signal.order_price_strategy[signal.signal_type];

  // 기준 가격 선택
  let basePrice = 0;

  switch (strategy.type) {
    case 'best_ask':
      basePrice = signal.sell_price;  // 매도 1호가
      break;
    case 'best_bid':
      basePrice = signal.buy_price;   // 매수 1호가
      break;
    case 'mid_price':
      basePrice = signal.current_price;  // 중간가
      break;
    case 'market':
      basePrice = null;  // 시장가
      break;
    default:
      basePrice = signal.signal_type === 'buy' ? signal.sell_price : signal.buy_price;
  }

  // offset 적용
  const orderPrice = basePrice ? Math.round(basePrice + (strategy.offset || 0)) : null;
  const orderMethod = basePrice === null ? 'MARKET' : 'LIMIT';

  console.log(`[${signal.signal_type}] ${signal.stock_code}: 기준=${basePrice}, offset=${strategy.offset}, 주문가=${orderPrice}`);

  results.push({
    json: {
      ...signal,
      order_price: orderPrice,
      order_method: orderMethod
    }
  });
}

return results;
```

### 9. 신호 저장 (trading_signals)
```json
{
  "parameters": {
    "method": "POST",
    "url": "={{$json.SUPABASE_URL}}/rest/v1/trading_signals",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\"stock_code\": {{JSON.stringify($json.stock_code)}}, \"stock_name\": {{JSON.stringify($json.stock_name)}}, \"signal_type\": {{JSON.stringify($json.signal_type)}}, \"strategy_id\": {{JSON.stringify($json.strategy_id)}}, \"strategy_name\": {{JSON.stringify($json.strategy_name)}}, \"current_price\": {{$json.current_price}}, \"change_rate\": {{$json.change_rate}}, \"confidence\": 75, \"status\": \"pending\"}",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{$json.SUPABASE_ANON_KEY}}"
        },
        {
          "name": "Authorization",
          "value": "={{\"Bearer \" + $json.SUPABASE_ANON_KEY}}"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        },
        {
          "name": "Prefer",
          "value": "return=representation"
        }
      ]
    }
  },
  "name": "신호 저장",
  "type": "n8n-nodes-base.httpRequest"
}
```

### 10. Kiwoom 토큰 발급
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://mockapi.kiwoom.com/oauth2/token",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\"grant_type\": \"client_credentials\", \"appkey\": \"S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU\", \"secretkey\": \"tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA\"}",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Content-Type",
          "value": "application/json;charset=UTF-8"
        }
      ]
    }
  },
  "name": "키움 토큰 발급",
  "type": "n8n-nodes-base.httpRequest"
}
```

### 11. Kiwoom 주문 실행
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://mockapi.kiwoom.com/api/dostk/order",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\"stk_cd\": {{JSON.stringify($node[\"주문 가격 계산\"].json.stock_code)}}, \"ord_qty\": \"10\", \"ord_prc\": {{$node[\"주문 가격 계산\"].json.order_price ? JSON.stringify(String($node[\"주문 가격 계산\"].json.order_price)) : '\"0\"'}}, \"ord_type\": {{$node[\"주문 가격 계산\"].json.signal_type === 'buy' ? '\"1\"' : '\"2\"'}}, \"ord_condition\": {{$node[\"주문 가격 계산\"].json.order_method === 'MARKET' ? '\"1\"' : '\"0\"'}}}",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Content-Type",
          "value": "application/json;charset=UTF-8"
        },
        {
          "name": "authorization",
          "value": "={{\"Bearer \" + $node[\"키움 토큰 발급\"].json.token}}"
        },
        {
          "name": "api-id",
          "value": "ka10005"
        }
      ]
    }
  },
  "name": "주문 실행",
  "type": "n8n-nodes-base.httpRequest"
}
```

### 12. 주문 결과 저장 (orders)
```json
{
  "parameters": {
    "method": "POST",
    "url": "={{$node[\"주문 가격 계산\"].json.SUPABASE_URL}}/rest/v1/orders",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\"signal_id\": {{JSON.stringify($node[\"신호 저장\"].json.id)}}, \"strategy_id\": {{JSON.stringify($node[\"주문 가격 계산\"].json.strategy_id)}}, \"stock_code\": {{JSON.stringify($node[\"주문 가격 계산\"].json.stock_code)}}, \"stock_name\": {{JSON.stringify($node[\"주문 가격 계산\"].json.stock_name)}}, \"order_type\": {{JSON.stringify($node[\"주문 가격 계산\"].json.signal_type.toUpperCase())}}, \"order_method\": {{JSON.stringify($node[\"주문 가격 계산\"].json.order_method)}}, \"quantity\": 10, \"order_price\": {{$node[\"주문 가격 계산\"].json.order_price || 0}}, \"status\": \"PENDING\", \"api_response\": {{JSON.stringify($json)}}}",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "={{$node[\"주문 가격 계산\"].json.SUPABASE_ANON_KEY}}"
        },
        {
          "name": "Authorization",
          "value": "={{\"Bearer \" + $node[\"주문 가격 계산\"].json.SUPABASE_ANON_KEY}}"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        },
        {
          "name": "Prefer",
          "value": "return=representation"
        }
      ]
    }
  },
  "name": "주문 결과 저장",
  "type": "n8n-nodes-base.httpRequest"
}
```

## 노드 연결 순서

```
5분마다 실행
  ↓
환경변수 설정
  ↓
활성 전략 조회
  ↓
유니버스 종목 추출
  ↓
현재가 조회 (각 종목)
  ↓
데이터 병합
  ↓
매수/매도 신호 생성
  ↓
주문 가격 계산
  ↓
신호 저장
  ↓
키움 토큰 발급
  ↓
주문 실행
  ↓
주문 결과 저장
```

## 다음 단계

1. n8n에서 새 워크플로우 생성
2. 위 노드들을 순서대로 추가
3. 테스트 (신호 생성 확인)
4. 실제 주문 테스트 (소량으로)
