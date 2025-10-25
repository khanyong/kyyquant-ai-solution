# stock_metadata 활용 종목명 표시 수정 가이드

## 🎯 해결 방안

`stock_metadata` 테이블에 종목코드와 종목명이 있으므로 이를 활용합니다.

## 📝 적용 순서

### 1️⃣ 기존 데이터 즉시 수정 (Supabase)

**파일**: `supabase/update_stock_names_from_metadata.sql`

```sql
-- stock_metadata에서 종목명 가져와서 kw_price_current 업데이트
UPDATE kw_price_current kpc
SET stock_name = sm.name
FROM stock_metadata sm
WHERE kpc.stock_code = sm.code
  AND (kpc.stock_name IS NULL OR kpc.stock_name = kpc.stock_code);
```

**실행 방법**:
1. Supabase Dashboard → SQL Editor
2. 위 SQL 실행
3. 결과 확인:
   ```sql
   SELECT stock_code, stock_name, current_price
   FROM kw_price_current
   WHERE stock_name != stock_code
   LIMIT 10;
   ```

**예상 결과**:
- 1000개 중 `stock_metadata`에 있는 종목들의 `stock_name`이 업데이트됨
- 즉시 프론트엔드에서 종목명 확인 가능

---

### 2️⃣ n8n 워크플로우 수정 (v20)

**수정 위치**: "조건 체크 및 신호 생성" 노드 (Code 노드)

**Before** (Line 227):
```javascript
// 종목명은 종목코드로 대체 (키움 API에서 제공하지 않음)
const stockName = kiwoomResponse.stk_nm || stockCode;
```

**After**:
```javascript
// stock_metadata 테이블에서 종목명 조회
let stockName = stockCode; // 기본값

try {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/stock_metadata?code=eq.${stockCode}&select=name`,
    {
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
      }
    }
  );

  const data = await response.json();
  if (data && data.length > 0 && data[0].name) {
    stockName = data[0].name;
  }
} catch (error) {
  console.error('Failed to fetch stock name:', error);
}
```

**전체 코드**: `n8n_signal_generation_code_with_stock_metadata.js` 파일 참고

---

### 3️⃣ n8n에서 적용

**방법 A: UI에서 직접 수정**

1. n8n Dashboard 접속
2. "자동매매 모니터링 v19" 워크플로우 열기
3. "조건 체크 및 신호 생성" 노드 클릭
4. JavaScript 코드 전체 교체:
   - `n8n_signal_generation_code_with_stock_metadata.js` 내용 복사
   - 노드의 Code 필드에 붙여넣기
5. "Save" 클릭
6. 워크플로우 이름 변경: "자동매매 모니터링 v20 (stock_metadata 활용)"

**방법 B: JSON 파일로 적용**

1. `auto-trading-with-capital-validation-v19.json` 복사 → v20
2. Line 227의 `jsCode` 필드를 새 코드로 교체
3. Line 2의 `name` 필드 수정:
   ```json
   "name": "자동매매 모니터링 v20 (stock_metadata 활용)"
   ```
4. n8n에서 Import

---

## 🧪 테스트

### 1. 기존 데이터 확인 (SQL 실행 후)

```sql
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 10;
```

**예상**:
```
005930 | 삼성전자   | 70000 | 0.00
000660 | SK하이닉스 | 135000 | 0.00
```

프론트엔드 새로고침 → 종목명 즉시 표시됨 ✅

### 2. 새 데이터 확인 (v20 실행 후)

1. v20 워크플로우 수동 실행
2. Supabase에서 최신 데이터 확인:
   ```sql
   SELECT stock_code, stock_name, updated_at
   FROM kw_price_current
   WHERE updated_at > NOW() - INTERVAL '10 minutes'
   ORDER BY updated_at DESC
   LIMIT 5;
   ```

3. 프론트엔드 확인:
   - 자동매매 탭 → 실시간 시장 모니터링
   - 종목명 정상 표시 확인

---

## ✅ 체크리스트

- [ ] Supabase SQL 실행 (`update_stock_names_from_metadata.sql`)
- [ ] 기존 데이터 종목명 확인 (Supabase)
- [ ] 프론트엔드 새로고침하여 즉시 확인
- [ ] n8n v20 워크플로우 생성 (신호 생성 노드 수정)
- [ ] v19 비활성화, v20 활성화
- [ ] v20 수동 실행 테스트
- [ ] 새 데이터 종목명 확인

---

## 🎯 최종 결과

**기존 데이터**: SQL 1회 실행 → 즉시 종목명 표시 ✅
**새 데이터**: v20 워크플로우 → 자동으로 종목명 저장 ✅

**상승/하락/보합 종목 수**: 등락률 계산 문제는 별도 해결 필요 (CHANGE_RATE_FIX_GUIDE.md 참고)
