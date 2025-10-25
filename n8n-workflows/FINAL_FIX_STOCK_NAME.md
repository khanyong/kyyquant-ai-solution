# 종목명 표시 문제 최종 해결 방안

## 🔴 문제 원인

키움 호가 조회 API (`/api/dostk/mrkcond`)는 **종목명(`stk_nm`) 필드를 제공하지 않습니다.**

**현재 코드** (Line 227):
```javascript
const stockName = kiwoomResponse.stk_nm || stockCode;
```
결과: `stk_nm`이 없어서 `stockCode`가 `stock_name`에 저장됨

## ✅ 해결 방법 3가지

### 방법 1: 하드코딩 종목 매핑 (즉시 적용 가능)

**장점**: 즉시 적용, n8n 워크플로우만 수정
**단점**: 전체 종목 커버 불가, 유지보수 필요

**수정 위치**: "신호 생성" 노드 (Line 227)

```javascript
// 종목명 매핑 테이블 추가
const STOCK_NAME_MAP = {
  '005930': '삼성전자',
  '000660': 'SK하이닉스',
  '035720': '카카오',
  '035420': '네이버',
  '051910': 'LG화학',
  '006400': '삼성SDI',
  '003550': 'LG',
  '055550': '신한지주',
  '105560': 'KB금융',
  '005380': '현대차',
  '000270': '기아',
  '207940': '삼성바이오로직스',
  '068270': '셀트리온',
  '028260': '삼성물산',
  '012330': '현대모비스',
  // ... 필요한 종목 추가
};

// 종목명 조회
const stockName = STOCK_NAME_MAP[stockCode] || stockCode;
```

### 방법 2: Supabase kw_stock_master 조회 (추천)

**장점**: 전체 종목 커버 가능, 동적 업데이트
**단점**: API 호출 추가

**n8n 워크플로우에 노드 추가**:

1. **"등락가/률 계산" 노드 다음에 새 노드 추가**
   - 이름: "종목명 조회"
   - 타입: Code (JavaScript)

```javascript
const item = $input.item.json;
const stockCode = item.stock_code;
const supabaseUrl = item.SUPABASE_URL;
const supabaseKey = item.SUPABASE_ANON_KEY;

try {
  // kw_stock_master에서 종목명 조회
  const response = await fetch(
    `${supabaseUrl}/rest/v1/kw_stock_master?stock_code=eq.${stockCode}&select=stock_name`,
    {
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`
      }
    }
  );

  const data = await response.json();
  const stockName = (data && data.length > 0) ? data[0].stock_name : stockCode;

  return {
    ...item,
    stock_name: stockName
  };
} catch (error) {
  console.error('Failed to fetch stock name:', error);
  // 에러 시 종목코드 사용
  return {
    ...item,
    stock_name: stockCode
  };
}
```

2. **연결 순서 변경**:
   ```
   등락가/률 계산 → 종목명 조회 → Supabase에 시세 저장
   ```

### 방법 3: kw_stock_master 전체 데이터 채우기 (근본 해결)

**장점**: 가장 깔끔한 해결, 다른 기능에서도 활용 가능
**단점**: 초기 데이터 수집 필요

**단계**:

1. **전체 종목 리스트 다운로드**
   - KRX 정보데이터시스템: http://data.krx.co.kr
   - 상장법인목록 → CSV 다운로드

2. **Supabase에 일괄 INSERT**
   ```sql
   -- CSV 데이터를 기반으로 INSERT
   INSERT INTO kw_stock_master (stock_code, stock_name, market, sector_name)
   VALUES
     ('005930', '삼성전자', 'KOSPI', '전기전자'),
     ('000660', 'SK하이닉스', 'KOSPI', '전기전자'),
     -- ... (전체 종목)
   ON CONFLICT (stock_code)
   DO UPDATE SET
     stock_name = EXCLUDED.stock_name,
     updated_at = CURRENT_TIMESTAMP;
   ```

3. **방법 2 적용**

## 🎯 추천 적용 순서

### 단계 1: 즉시 적용 (방법 1)

주요 종목 10~20개만 하드코딩하여 즉시 테스트

### 단계 2: 중기 적용 (방법 2)

kw_stock_master 조회 노드 추가

### 단계 3: 장기 적용 (방법 3)

전체 종목 마스터 데이터 수집 및 DB 채우기

## 📝 v20 워크플로우 (방법 1 적용)

**수정 내용**:
- "신호 생성" 노드에 종목명 매핑 테이블 추가

**적용 방법**:
1. v19 JSON 파일 복사 → v20
2. Line 227의 JavaScript 코드 수정
3. n8n에서 Import

## 🧪 테스트

v20 적용 후:
```sql
SELECT stock_code, stock_name, current_price
FROM kw_price_current
WHERE stock_code IN ('005930', '000660', '035720')
ORDER BY updated_at DESC
LIMIT 3;
```

**예상 결과**:
```
005930 | 삼성전자   | 70000
000660 | SK하이닉스 | 135000
035720 | 카카오     | 48500
```
