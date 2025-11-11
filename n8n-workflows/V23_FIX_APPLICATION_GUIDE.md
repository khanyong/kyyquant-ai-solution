# n8n 워크플로우 V23 Fix 적용 가이드

## 문제 상황
"조건 체크 및 신호 생성" 노드에서 `stock_code`, `strategy_id`, `strategy_name`이 모두 빈 문자열("")로 출력됨

## 원인
"데이터 병합" 노드의 코드가 v23-fixed-v2 버전으로 업데이트되지 않았음

## 해결방법 (2가지 중 선택)

### 방법 1: 워크플로우 JSON 파일 재임포트 (권장)

1. n8n 웹 인터페이스 접속
2. 현재 워크플로우 삭제 또는 이름 변경
3. "Import from File" 클릭
4. 파일 선택: `d:\Dev\auto_stock\n8n-workflows\auto-trading-with-capital-validation-v23-fixed-v2.json`
5. 임포트 완료 후 "Save" 클릭
6. 워크플로우 재실행

### 방법 2: "데이터 병합" 노드 코드 수동 업데이트

1. n8n에서 현재 워크플로우 열기
2. "데이터 병합" 노드 더블클릭
3. 아래 코드를 전체 복사하여 붙여넣기:

```javascript
// 모든 입력 아이템 가져오기
const allItems = $input.all();

// 첫 번째 입력: 종목 코드 추출 노드의 데이터
// 두 번째 입력: 키움 호가 조회 응답
const originalData = allItems[0].json;
const kiwoomData = allItems[1].json;

console.log('🔄 데이터 병합 시작');
console.log('📋 Original stock_code:', originalData.stock_code);
console.log('📋 Original strategy_id:', originalData.strategy_id);
console.log('📋 Original strategy_name:', originalData.strategy_name);

// 원본 데이터를 _original_ 접두사로 보존
const mergedData = {
  // 원본 데이터 보존 (접두사 추가)
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

console.log('✅ Merged data keys count:', Object.keys(mergedData).length);
console.log('✅ _original_stock_code:', mergedData._original_stock_code);
console.log('✅ _original_strategy_id:', mergedData._original_strategy_id);

return mergedData;
```

4. "Save" 클릭
5. 워크플로우 재실행

## 검증 방법

워크플로우 실행 후 콘솔 로그에서 다음 내용 확인:

### 성공 시 보여야 할 로그:
```
[Node: "데이터 병합"] '🔄 데이터 병합 시작'
[Node: "데이터 병합"] '📋 Original stock_code:' '005930'  // 실제 종목코드
[Node: "데이터 병합"] '📋 Original strategy_id:' 'uuid-값'
[Node: "데이터 병합"] '📋 Original strategy_name:' '전략이름'
[Node: "데이터 병합"] '✅ Merged data keys count:' 71
[Node: "데이터 병합"] '✅ _original_stock_code:' '005930'
[Node: "데이터 병합"] '✅ _original_strategy_id:' 'uuid-값'
[Node: "조건 체크 및 신호 생성"] '📋 Stock code:' '005930'  // 빈 문자열 아님!
[Node: "조건 체크 및 신호 생성"] '📋 Strategy:' '전략이름'  // 빈 문자열 아님!
```

### 실패 시 (현재 상태):
```
[Node: "데이터 병합"] '📦 Original data keys:' Array(71)
[Node: "조건 체크 및 신호 생성"] '📋 Stock code:' ''  // 빈 문자열
[Node: "조건 체크 및 신호 생성"] '📋 Strategy:' ''  // 빈 문자열
```

## 추가 확인사항

1. **백엔드 서버 실행 확인**
   - v23에서는 지표 계산 API를 제거했으므로 백엔드 서버가 필수는 아님
   - 하지만 향후 확장을 위해 실행 권장: `cd d:\Dev\auto_stock\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`

2. **Supabase RPC 함수 확인**
   - `fix_rpc_strategy_data.sql` 이미 실행 완료
   - RPC 함수가 strategy_id, strategy_name, entry_conditions, exit_conditions 반환 확인됨

3. **환경변수 확인**
   - SUPABASE_URL: https://hznkyaomtrpzcayayayh.supabase.co
   - KIWOOM_APP_KEY: S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU
   - KIWOOM_IS_DEMO: true (모의투자)

## 다음 단계

워크플로우 수정 후:
1. n8n 워크플로우 재실행
2. 콘솔 로그 확인 (위의 성공 로그 패턴 확인)
3. `kw_price_current` 테이블에 데이터 저장 확인
4. 프론트엔드 "자동매매 탭"에서 상승종목/하락종목 개수 확인

## 문제 해결

### 여전히 빈 문자열이 출력되는 경우:
1. 브라우저 캐시 클리어 후 n8n 재접속
2. n8n 서버 재시작: `docker restart n8n`
3. 워크플로우를 새 이름으로 복제 후 재실행

### Console.log가 보이지 않는 경우:
1. n8n 웹 인터페이스에서 "Browser Console" (F12) 열기
2. 워크플로우 실행 중 Console 탭 확인
3. 또는 n8n Docker 컨테이너 로그 확인: `docker logs -f n8n`
