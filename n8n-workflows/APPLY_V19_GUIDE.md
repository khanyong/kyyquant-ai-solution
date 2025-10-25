# 자동매매 모니터링 v19 적용 가이드

## 📋 변경 사항

### v18 → v19 주요 수정
- ✅ `stock_name` 필드 추가하여 종목명 저장
- ✅ 키움 API의 `stk_nm` 필드 활용

## 🚀 적용 순서

### 1. Supabase 테이블 수정 (완료 ✅)

```sql
-- 이미 실행 완료
ALTER TABLE kw_price_current
ADD COLUMN IF NOT EXISTS stock_name VARCHAR(100);
```

### 2. n8n 워크플로우 Import

#### 방법 A: n8n UI에서 Import (권장)

1. **n8n Dashboard 접속**
   ```
   http://192.168.50.150:5678
   ```

2. **새 워크플로우 Import**
   - 우측 상단 메뉴 → "Import from File" 클릭
   - `auto-trading-with-capital-validation-v19.json` 선택
   - Import 완료

3. **기존 v18 워크플로우 비활성화**
   - "자동매매 모니터링 v18" 워크플로우 열기
   - 우측 상단 Active 토글 OFF

4. **v19 워크플로우 활성화**
   - "자동매매 모니터링 v19" 워크플로우 열기
   - 우측 상단 Active 토글 ON
   - "Save" 클릭

#### 방법 B: Docker Container에서 직접 교체

```bash
# NAS SSH 접속 후
cd /volume1/docker/n8n/.n8n/workflows

# 백업
cp auto-trading-with-capital-validation-v18.json auto-trading-with-capital-validation-v18.json.backup

# v19로 교체
cp auto-trading-with-capital-validation-v19.json auto-trading-with-capital-validation-v18.json

# n8n 재시작
docker restart n8n
```

### 3. 테스트 실행

1. **수동 실행**
   - v19 워크플로우 열기
   - 좌측 상단 "Execute Workflow" 클릭
   - 실행 결과 확인

2. **Supabase 데이터 확인**
   ```sql
   SELECT
     stock_code,
     stock_name,
     current_price,
     change_rate,
     updated_at
   FROM kw_price_current
   WHERE updated_at > NOW() - INTERVAL '10 minutes'
   ORDER BY updated_at DESC
   LIMIT 10;
   ```

   **예상 결과**:
   ```json
   {
     "stock_code": "005930",
     "stock_name": "삼성전자",  // ← 종목명 표시됨
     "current_price": 70000,
     "change_rate": 2.35,      // ← 0이 아닌 실제 값
     "updated_at": "2025-10-24 12:15:00"
   }
   ```

3. **화면 확인**
   - 프론트엔드 새로고침
   - 자동매매 탭 → 실시간 시장 모니터링
   - 종목명 정상 표시 확인
   - 상승/하락 종목 수 집계 확인

## 🔍 변경 내용 상세

### 수정된 부분

**파일**: `auto-trading-with-capital-validation-v19.json` (Line 296)

**Before**:
```json
{
  "stock_code": {{JSON.stringify($json.stock_code)}},
  "current_price": {{$json.current_price}},
  "change_price": {{$json.change_price}},
  "change_rate": {{$json.change_rate}},
  "volume": {{$json.volume || 0}},
  "high_52w": {{$json.sel_price || 0}},
  "low_52w": {{$json.buy_price || 0}},
  "market_cap": 0
}
```

**After**:
```json
{
  "stock_code": {{JSON.stringify($json.stock_code)}},
  "stock_name": {{JSON.stringify($json.stock_name || $json.stock_code)}},  // ← 추가
  "current_price": {{$json.current_price}},
  "change_price": {{$json.change_price}},
  "change_rate": {{$json.change_rate}},
  "volume": {{$json.volume || 0}},
  "high_52w": {{$json.sel_price || 0}},
  "low_52w": {{$json.buy_price || 0}},
  "market_cap": 0
}
```

### 데이터 흐름

```
키움 API 호출
  ↓
응답에서 stk_nm 추출 (신호 생성 노드)
  ↓
stock_name 필드로 전달
  ↓
Supabase kw_price_current 저장 ← 수정된 부분
  ↓
MarketMonitor.tsx에서 표시
```

## 🎯 해결되는 문제

- ✅ 종목명이 종목코드 대신 정상 표시 (예: "삼성전자")
- ✅ `kw_stock_master` 조인 불필요
- ✅ 실시간 구독 시에도 종목명 표시

## ⚠️ 주의사항

1. **등락률 문제는 별도 해결 필요**
   - 현재 v19는 종목명만 수정
   - 등락률 계산은 `CHANGE_RATE_FIX_GUIDE.md` 참고

2. **기존 데이터는 null 유지**
   - v19 적용 후 새로 수집되는 데이터만 종목명 포함
   - 기존 1000개 데이터는 `stock_name = null` 상태

3. **백업 권장**
   - 적용 전 v18 워크플로우 Export하여 백업

## 📞 문제 발생 시

1. **종목명이 여전히 코드로 표시**
   - n8n 워크플로우 활성화 확인
   - 실행 로그에서 에러 확인
   - `$json.stock_name` 값 확인

2. **워크플로우 실행 실패**
   - Supabase 연결 확인
   - API 키 확인
   - 로그 확인: n8n Dashboard → Executions

3. **데이터 저장 안 됨**
   - Supabase RLS 정책 확인
   - 테이블 권한 확인
