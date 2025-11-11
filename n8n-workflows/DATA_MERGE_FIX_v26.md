# 데이터 병합 노드 수정 - v26 (최종 해결책)

## 문제 분석

**에러**: `데이터 병합 노드에 105개의 입력이 들어왔습니다. 2개여야 합니다.`

**원인**:
- "종목 코드 추출" 노드가 105개 아이템 생성
- n8n은 각 아이템을 개별적으로 다음 노드에 전달
- `$input.all()`은 현재 배치의 모든 입력을 가져오는데, 105개가 한번에 들어옴
- 우리가 원하는 것: 각 아이템마다 "종목 코드 추출"의 원본 데이터 + "키움 호가 조회"의 응답 데이터

## 해결책: 노드 참조 방식 사용

"데이터 병합" 노드에서 다음 코드를 사용하세요:

```javascript
// ============================================================================
// 데이터 병합 노드 - v26 (노드 직접 참조 방식)
// 목적: 종목 코드 추출 노드의 원본 데이터를 보존하면서 키움 API 응답과 병합
// ============================================================================

// 현재 아이템의 키움 호가 조회 응답 데이터
const kiwoomData = $input.item.json;

// 종목 코드 추출 노드의 원본 데이터를 직접 참조
// pairedItem을 통해 현재 아이템에 대응하는 원본 데이터를 가져옴
const pairedItemIndex = $input.item.pairedItem;
const originalData = $('종목 코드 추출').item.json(pairedItemIndex);

console.log('🔄 데이터 병합 시작');
console.log('📋 Original data from 종목 코드 추출:');
console.log('  - stock_code:', originalData.stock_code);
console.log('  - strategy_id:', originalData.strategy_id);
console.log('  - strategy_name:', originalData.strategy_name);

console.log('📋 Kiwoom API response:');
console.log('  - stk_cd:', kiwoomData.stk_cd);
console.log('  - Keys count:', Object.keys(kiwoomData).length);

// 원본 데이터를 _original_ 접두사로 보존하면서 키움 데이터 병합
const mergedData = {
  // 원본 데이터 보존 (나중에 Supabase 저장 시 사용)
  _original_stock_code: originalData.stock_code,
  _original_strategy_id: originalData.strategy_id,
  _original_strategy_name: originalData.strategy_name,
  _original_entry_conditions: originalData.entry_conditions,
  _original_exit_conditions: originalData.exit_conditions,
  _original_SUPABASE_URL: originalData.SUPABASE_URL,
  _original_SUPABASE_ANON_KEY: originalData.SUPABASE_ANON_KEY,
  _original_BACKEND_URL: originalData.BACKEND_URL,

  // 키움 API 응답 데이터 병합
  ...kiwoomData
};

console.log('✅ 데이터 병합 완료');
console.log('✅ _original_stock_code:', mergedData._original_stock_code);
console.log('✅ _original_strategy_id:', mergedData._original_strategy_id);
console.log('✅ stk_cd (키움):', mergedData.stk_cd);

return mergedData;
```

## 수정 방법

### 1단계: n8n에서 워크플로우 열기
현재 실행중인 워크플로우를 엽니다.

### 2단계: 노드 연결 확인
**반드시 다음과 같이 연결:**

```
종목 코드 추출
  └─→ 키움 호가 조회

키움 호가 조회
  └─→ 데이터 병합

데이터 병합
  └─→ 조건 체크 및 신호 생성
```

**중요**: "종목 코드 추출" → "데이터 병합" **직접 연결 제거**
- v25에서 추가했던 직접 연결을 **삭제**해야 합니다
- "키움 호가 조회"를 거쳐서만 "데이터 병합"으로 가야 합니다

### 3단계: 데이터 병합 노드 코드 교체
1. "데이터 병합" 노드 더블클릭
2. 기존 코드 전체 삭제
3. 위의 v26 코드 복사하여 붙여넣기
4. 저장

### 4단계: 테스트 실행
워크플로우 실행 후 콘솔 확인:

**정상 로그:**
```
[Node: "데이터 병합"] '🔄 데이터 병합 시작'
[Node: "데이터 병합"] '📋 Original data from 종목 코드 추출:'
[Node: "데이터 병합"] '  - stock_code:' '005930'
[Node: "데이터 병합"] '  - strategy_id:' 'abc-123'
[Node: "데이터 병합"] '✅ _original_stock_code:' '005930'
```

## 기술적 설명

### pairedItem이란?
n8n에서 각 아이템은 `pairedItem` 속성을 가지며, 이는 이전 노드의 어떤 아이템에서 왔는지를 추적합니다.

**데이터 흐름:**
1. "종목 코드 추출": 105개 아이템 생성 (인덱스 0~104)
2. "키움 호가 조회": 각 아이템마다 API 호출, 응답과 함께 `pairedItem` 유지
3. "데이터 병합":
   - `$input.item.json` → 현재 아이템 (키움 응답)
   - `$input.item.pairedItem` → 원본 아이템 인덱스
   - `$('종목 코드 추출').item.json(pairedItemIndex)` → 해당 인덱스의 원본 데이터

## 주의사항

1. **직접 연결 제거 필수**: "종목 코드 추출" → "데이터 병합" 연결이 있으면 안 됨
2. **배치 간격**: "키움 호가 조회" 노드의 Batch Interval이 30000ms인지 확인
3. **CORS 에러 무시**: workflow.bll-pro.com 관련 에러는 무시

## 트러블슈팅

### 에러: "pairedItem is undefined"
**원인**: 키움 호가 조회 노드가 pairedItem 정보를 전달하지 않음

**해결**:
```javascript
// pairedItem이 undefined인 경우 대체 방법
const pairedItemIndex = $input.item.pairedItem || 0;
const originalData = $('종목 코드 추출').first().json;
```

### 에러: "Cannot read property 'stock_code' of undefined"
**원인**: 원본 데이터를 찾을 수 없음

**해결**: 콘솔 로그로 디버깅
```javascript
console.log('pairedItem:', $input.item.pairedItem);
console.log('종목 코드 추출 all items:', $('종목 코드 추출').all());
```
