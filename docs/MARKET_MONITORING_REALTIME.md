# 📊 실시간 시장 모니터링 설정 가이드 (기존 테이블 활용)

## ✅ 결론: 새 테이블 생성 불필요!

기존 `kw_price_current` 테이블을 그대로 사용합니다.

---

## 📋 기존 테이블 구조

### `kw_price_current` 테이블

```sql
stock_code            VARCHAR (PK)  -- 종목코드
current_price         NUMERIC       -- 현재가
change_price          NUMERIC       -- 등락 금액
change_rate           NUMERIC       -- 등락률
volume                BIGINT        -- 거래량
trading_value         BIGINT        -- 거래대금
high_52w              NUMERIC       -- 52주 최고가
low_52w               NUMERIC       -- 52주 최저가
market_cap            BIGINT        -- 시가총액
shares_outstanding    BIGINT        -- 발행주식수
foreign_ratio         NUMERIC       -- 외국인 비율
updated_at            TIMESTAMP     -- 업데이트 시간
```

### ✅ 필수 컬럼 모두 존재
- ✅ `stock_code` - 종목코드
- ✅ `current_price` - 현재가
- ✅ `change_rate` - 등락률
- ✅ `volume` - 거래량
- ✅ `updated_at` - 시간

---

## 🔧 설정 방법

### 1. Supabase Realtime 활성화

#### Supabase Dashboard 접속
https://supabase.com/dashboard/project/hznkyaomtrpzcayayayh

#### Database → Replication 탭
- `kw_price_current` 테이블 찾기
- **UPDATE** 이벤트 활성화 ✅ (중요: INSERT가 아닌 UPDATE)
- Save 클릭

---

### 2. n8n 워크플로우 설정 (선택사항)

n8n으로 `kw_price_current` 테이블을 업데이트하려면:

#### n8n 워크플로우: "시장 데이터 업데이트 (1분)"

**Node 1: Schedule Trigger**
- Interval: 1분

**Node 2: 장시간 체크**
- 09:00 ~ 15:30

**Node 3: 종목 리스트**
```javascript
const stocks = ['005930', '000660', '035420', '051910'];
return stocks.map(code => ({json: {stock_code: code}}));
```

**Node 4: 백엔드 API 시세 조회**
- URL: `http://192.168.50.150:8080/api/market/price/{{$json.stock_code}}`

**Node 5: Supabase UPSERT** ⚠️ 중요
- Operation: **UPSERT** (INSERT or UPDATE)
- Table: `kw_price_current`
- Conflict Target: `stock_code`
- Columns:
  - `stock_code`: `={{$json.stock_code}}`
  - `current_price`: `={{$json.current_price}}`
  - `change_price`: `={{$json.change}}`
  - `change_rate`: `={{$json.change_rate}}`
  - `volume`: `={{$json.volume}}`
  - `updated_at`: `={{$now}}`

---

### 3. 프론트엔드 확인

#### 접속
http://localhost:3000

#### 확인 사항
1. 로그인
2. "실시간 신호" 탭 클릭
3. 상단에 "시장 모니터링 (n8n)" 섹션 확인
4. 종목 리스트가 표시되는지 확인

---

## 📊 데이터 흐름

```
┌─────────────────────────────────────┐
│  n8n 워크플로우 (1분 주기)           │
│  ├─ 백엔드 API 시세 조회            │
│  └─ Supabase UPSERT                │
│      └─ kw_price_current 테이블     │
└──────────────┬──────────────────────┘
               │
               ↓ UPDATE 이벤트
┌─────────────────────────────────────┐
│  Supabase Realtime                  │
│  (UPDATE 이벤트 전송)                │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  프론트엔드 SignalMonitor           │
│  └─ 실시간 자동 업데이트            │
└─────────────────────────────────────┘
```

---

## 🧪 테스트

### 1. 기존 데이터 확인
```sql
-- 현재 저장된 데이터 확인
SELECT
    stock_code,
    current_price,
    change_rate,
    volume,
    updated_at
FROM kw_price_current
ORDER BY updated_at DESC
LIMIT 10;
```

### 2. 수동 업데이트 테스트
```sql
-- 특정 종목 업데이트 (테스트용)
UPDATE kw_price_current
SET
    current_price = 75000,
    change_rate = 2.5,
    volume = 1000000,
    updated_at = NOW()
WHERE stock_code = '005930';
```

→ 프론트엔드에서 삼성전자 데이터가 즉시 업데이트되는지 확인

### 3. Realtime 연결 확인
- 브라우저 개발자 도구 → Console
- `📊 New market data: ...` 로그 확인

---

## 🔧 문제 해결

### ❌ 데이터가 표시되지 않을 때

#### 1. Realtime 이벤트 확인
```sql
-- Realtime이 활성화되었는지 확인
SELECT * FROM pg_publication_tables
WHERE pubname = 'supabase_realtime';
```

#### 2. 데이터 존재 여부 확인
```sql
SELECT COUNT(*) FROM kw_price_current;
```

결과가 0이면 데이터가 없음 → n8n 워크플로우 실행 필요

#### 3. RLS 정책 확인
```sql
-- 읽기 권한 확인
SELECT * FROM pg_policies
WHERE tablename = 'kw_price_current';
```

---

## 💡 기존 테이블 활용의 장점

✅ **즉시 사용 가능** - 새 테이블 생성 불필요
✅ **데이터 중복 없음** - 단일 소스 데이터
✅ **유지보수 간편** - 하나의 테이블만 관리
✅ **추가 비용 없음** - 스토리지 절약

---

## 📌 참고사항

### 고가/저가 컬럼 변경
- ❌ `high`, `low` (당일 고가/저가) → 테이블에 없음
- ✅ `high_52w`, `low_52w` (52주 고가/저가) → 표시 중

→ 당일 고가/저가가 필요하면 `kw_price_minute` 테이블에서 집계 필요

### 종목명 추가
현재 `kw_price_current`에는 `stock_code`만 있음.
종목명이 필요하면 `kw_stock_master` 테이블과 JOIN:

```sql
SELECT
    p.stock_code,
    m.name as stock_name,
    p.current_price,
    p.change_rate,
    p.volume
FROM kw_price_current p
LEFT JOIN kw_stock_master m ON p.stock_code = m.code
ORDER BY p.updated_at DESC
LIMIT 20;
```

---

## ✅ 완료!

이제 기존 `kw_price_current` 테이블을 활용하여 실시간 시장 모니터링이 가능합니다! 🎉
