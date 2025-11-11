# n8n 워크플로우 "종목 코드 추출" 노드 수정 가이드

## 문제
RPC 함수가 이제 올바르게 모든 필드를 반환하지만, `filtered_stocks`가 **jsonb** 타입이므로 JavaScript에서 객체로 처리됩니다.

## 해결방법

n8n 워크플로우 편집기에서 **"종목 코드 추출"** 노드를 열고 아래 코드로 **전체 교체**하세요:

```javascript
const items = $input.all();
const results = [];

const envVars = $('환경변수 설정').first().json;
const tokenData = $('키움 토큰 발급').first().json;

for (const item of items) {
  const strategy = item.json;
  let stockCodes = [];

  // filtered_stocks가 jsonb 타입인 경우 처리
  if (strategy.filtered_stocks) {
    if (Array.isArray(strategy.filtered_stocks)) {
      // 이미 배열인 경우 (JavaScript에서 파싱됨)
      stockCodes = strategy.filtered_stocks.filter(code => code && typeof code === 'string');
    } else if (typeof strategy.filtered_stocks === 'object') {
      // jsonb 객체인 경우 배열로 변환
      stockCodes = Object.values(strategy.filtered_stocks).filter(code => code && typeof code === 'string');
    }
  }

  console.log(`📊 Strategy: ${strategy.strategy_name}, Stock count: ${stockCodes.length}`);

  stockCodes.forEach(stockCode => {
    results.push({
      json: {
        strategy_id: strategy.strategy_id,
        strategy_name: strategy.strategy_name,
        entry_conditions: strategy.entry_conditions,
        exit_conditions: strategy.exit_conditions,
        stock_code: stockCode,
        access_token: tokenData.token,
        KIWOOM_APP_KEY: envVars.KIWOOM_APP_KEY,
        KIWOOM_APP_SECRET: envVars.KIWOOM_APP_SECRET,
        SUPABASE_URL: envVars.SUPABASE_URL,
        SUPABASE_ANON_KEY: envVars.SUPABASE_ANON_KEY,
        BACKEND_URL: envVars.BACKEND_URL
      }
    });
  });
}

console.log(`✅ Total items created: ${results.length}`);
return results;
```

## 변경 사항
1. `Array.isArray()` 체크 추가
2. jsonb 객체를 배열로 변환하는 로직 추가 (`Object.values()`)
3. 디버깅을 위한 콘솔 로그 추가

## 테스트
워크플로우를 저장하고 수동 실행하여 다음을 확인하세요:
- "종목 코드 추출" 노드 실행 로그에 종목 수가 표시됨
- "데이터 병합" 노드에서 `stock_code`가 비어있지 않음
- "시장 데이터 저장" 노드에서 데이터가 정상적으로 저장됨
