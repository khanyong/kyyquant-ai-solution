# 🔧 데이터 병합 노드 수동 수정 가이드

## ⚠️ 문제 상황
- 프론트엔드에 0개 상승종목, 0개 하락종목 표시
- `kw_price_current` 테이블에 데이터 저장 안됨
- 원인: "데이터 병합" 노드가 `stock_code`, `strategy_id` 등을 제대로 전달하지 못함

## ✅ 해결 방법: 데이터 병합 노드 코드 직접 수정

### 1단계: n8n 워크플로우 열기
1. n8n 웹 인터페이스 접속 (http://192.168.50.150:5678)
2. "자동매매 모니터링" 워크플로우 열기 (현재 실행중인 워크플로우)

### 2단계: 노드 연결 확인
**반드시 다음과 같이 연결되어 있어야 함:**

```
종목 코드 추출
  ├─→ 키움 호가 조회
  └─→ 데이터 병합

키움 호가 조회
  └─→ 데이터 병합

데이터 병합
  └─→ 조건 체크 및 신호 생성
```

**중요**: "데이터 병합" 노드는 **2개의 입력**을 받아야 합니다!
- Input 1: "종목 코드 추출" (직접 연결)
- Input 2: "키움 호가 조회" (응답 데이터)

### 3단계: 데이터 병합 노드 코드 교체

1. "데이터 병합" 노드 더블클릭하여 열기
2. 기존 코드 **전체 삭제**
3. 아래 코드를 **정확히 복사하여 붙여넣기**:

```javascript
// ============================================================================
// 데이터 병합 노드 - v23-fixed-v2
// 목적: 종목 코드 추출 노드의 원본 데이터를 보존하면서 키움 API 응답과 병합
// ============================================================================

// 모든 입력 아이템 가져오기
const allItems = $input.all();

console.log('🔄 데이터 병합 시작');
console.log('📊 Total inputs received:', allItems.length);

// 입력이 2개가 아닌 경우 에러
if (allItems.length !== 2) {
  console.error('❌ ERROR: Expected 2 inputs, got:', allItems.length);
  throw new Error(`데이터 병합 노드에 ${allItems.length}개의 입력이 들어왔습니다. 2개여야 합니다.`);
}

// 첫 번째 입력: 종목 코드 추출 노드의 원본 데이터
const originalData = allItems[0].json;

// 두 번째 입력: 키움 호가 조회 API 응답
const kiwoomData = allItems[1].json;

console.log('📋 Input 1 (종목 코드 추출):');
console.log('  - stock_code:', originalData.stock_code);
console.log('  - strategy_id:', originalData.strategy_id);
console.log('  - strategy_name:', originalData.strategy_name);

console.log('📋 Input 2 (키움 호가 조회):');
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
console.log('✅ Merged data keys count:', Object.keys(mergedData).length);
console.log('✅ _original_stock_code:', mergedData._original_stock_code);
console.log('✅ _original_strategy_id:', mergedData._original_strategy_id);
console.log('✅ stk_cd (키움):', mergedData.stk_cd);

return mergedData;
```

4. "Save" 또는 "저장" 버튼 클릭
5. 워크플로우 상단의 "Save" 버튼 클릭하여 전체 워크플로우 저장

### 4단계: 키움 호가 조회 노드 배치 간격 확인

1. "키움 호가 조회" 노드 더블클릭
2. "Options" 탭 선택
3. "Batching" 섹션:
   - **Batch Interval: 30000** (30초)
   - **Items per Batch: 1**
4. 저장

### 5단계: 테스트 실행

1. 워크플로우 "Execute Workflow" 버튼 클릭
2. 콘솔에서 다음 로그 확인:

**올바른 로그 예시:**
```
[Node: "데이터 병합"] '🔄 데이터 병합 시작'
[Node: "데이터 병합"] '📊 Total inputs received:' 2
[Node: "데이터 병합"] '📋 Input 1 (종목 코드 추출):'
[Node: "데이터 병합"] '  - stock_code:' '005930'
[Node: "데이터 병합"] '  - strategy_id:' 'abc-123-def-456'
[Node: "데이터 병합"] '✅ _original_stock_code:' '005930'
[Node: "데이터 병합"] '✅ _original_strategy_id:' 'abc-123-def-456'
```

**잘못된 로그 (수정 필요):**
```
[Node: "데이터 병합"] '❌ ERROR: Expected 2 inputs, got:' 1
```
→ 이 경우 2단계로 돌아가서 노드 연결을 다시 확인

### 6단계: 전체 실행 및 결과 확인

1. 워크플로우 전체 실행 (예상 시간: 105개 종목 × 30초 = 52분)
2. 완료 후 Supabase에서 확인:

```sql
-- 최근 저장된 데이터 확인
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate,
  signal_type,
  created_at
FROM kw_price_current
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 20;
```

3. 프론트엔드에서 확인:
   - "자동매매" 탭 → "시장 모니터링" 섹션
   - 상승종목: X개 (0이 아닌 숫자)
   - 하락종목: X개 (0이 아닌 숫자)
   - 등락률: X% (0%가 아닌 값)

## 🐛 문제 해결

### 문제 1: "Expected 2 inputs, got: 1" 에러
**원인**: 노드 연결이 잘못됨

**해결**:
1. "종목 코드 추출" 노드 클릭
2. 오른쪽 동그라미(출력 커넥터)를 "데이터 병합" 노드로 드래그하여 직접 연결
3. "키움 호가 조회" → "데이터 병합" 연결도 유지되어 있는지 확인

### 문제 2: "_original_stock_code: undefined" 로그
**원인**: "종목 코드 추출" 노드가 stock_code를 생성하지 못함

**해결**:
1. "종목 코드 추출" 노드의 콘솔 로그 확인
2. `filtered_stocks` 데이터가 올바른지 확인
3. 필요시 "자동매매 전략 조회" 노드 응답 확인

### 문제 3: 429 Too Many Requests 에러
**원인**: 배치 간격이 너무 짧음

**해결**:
1. "키움 호가 조회" 노드 Options → Batch Interval을 60000 (1분)으로 증가
2. 재실행

## ✅ 성공 기준

다음 조건이 모두 충족되면 성공:

1. ✅ 콘솔 로그에 `✅ _original_stock_code: '005930'` 같은 실제 값 표시
2. ✅ 콘솔 로그에 `✅ _original_strategy_id: 'uuid-값'` 표시
3. ✅ `kw_price_current` 테이블에 데이터 저장됨
4. ✅ 프론트엔드에서 0이 아닌 상승/하락 종목 수 표시

## 📝 참고사항

- **CORS 에러 무시**: `workflow.bll-pro.com` 관련 CORS 에러는 n8n 텔레메트리이므로 무시해도 됨
- **실행 시간**: 105개 종목 기준 약 52분 소요 (배치 간격 30초 기준)
- **데이터 흐름**: 종목 코드 추출 → 키움 호가 조회 → 데이터 병합 → 조건 체크 → Supabase 저장
