# 📊 시장 모니터링 시스템 설정 가이드

n8n 워크플로우를 통해 실시간 시장 데이터를 수집하고 프론트엔드에 표시하는 방법입니다.

## 📋 목차
1. [Supabase 테이블 생성](#1-supabase-테이블-생성)
2. [n8n 워크플로우 생성](#2-n8n-워크플로우-생성)
3. [프론트엔드 확인](#3-프론트엔드-확인)
4. [문제 해결](#4-문제-해결)

---

## 1. Supabase 테이블 생성

### 1-1. Supabase Dashboard 접속
https://supabase.com/dashboard/project/hznkyaomtrpzcayayayh

### 1-2. SQL Editor에서 테이블 생성

```sql
-- 시장 모니터링 데이터 테이블
CREATE TABLE IF NOT EXISTS market_monitoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    current_price NUMERIC NOT NULL,
    change_amount NUMERIC DEFAULT 0,
    change_rate NUMERIC DEFAULT 0,
    volume BIGINT DEFAULT 0,
    high NUMERIC DEFAULT 0,
    low NUMERIC DEFAULT 0,
    market_cap NUMERIC,
    monitored_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'n8n',
    metadata JSONB,

    -- 인덱스
    CONSTRAINT uk_stock_monitored UNIQUE (stock_code, monitored_at)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_market_monitoring_stock_code
    ON market_monitoring(stock_code);

CREATE INDEX IF NOT EXISTS idx_market_monitoring_monitored_at
    ON market_monitoring(monitored_at DESC);

-- RLS (Row Level Security) 설정
ALTER TABLE market_monitoring ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽을 수 있도록 설정
CREATE POLICY "Enable read access for all users"
    ON market_monitoring FOR SELECT
    USING (true);

-- n8n이나 서버에서만 쓸 수 있도록 설정 (service role key 필요)
CREATE POLICY "Enable insert for service role only"
    ON market_monitoring FOR INSERT
    WITH CHECK (true);

-- 오래된 데이터 자동 삭제 (선택사항 - 7일 이상 데이터)
-- 스케줄러 확장 필요: pg_cron
-- SELECT cron.schedule(
--   'delete-old-market-data',
--   '0 0 * * *', -- 매일 자정
--   $$DELETE FROM market_monitoring WHERE monitored_at < NOW() - INTERVAL '7 days'$$
-- );
```

### 1-3. Realtime 활성화

Supabase Dashboard → Database → Replication 탭
- `market_monitoring` 테이블에 대해 `INSERT` 이벤트 활성화

---

## 2. n8n 워크플로우 생성

### 2-1. n8n 접속
http://192.168.50.150:5678

### 2-2. 새 워크플로우 생성

**워크플로우 이름:** `시장 모니터링 (1분 주기)`

### 2-3. 노드 구성

#### 📌 Node 1: Schedule Trigger
- **노드 타입:** Schedule Trigger
- **설정:**
  - Interval: `minutes`
  - Minutes Between Executions: `1`

#### 📌 Node 2: 장시간 체크
- **노드 타입:** IF
- **조건:**
  ```javascript
  {{$now.format('HH:mm')}} >= 09:00 AND {{$now.format('HH:mm')}} <= 15:30
  ```
- **요일 체크:** 평일만 (월~금)

#### 📌 Node 3: 모니터링 종목 설정
- **노드 타입:** Code
- **코드:**
  ```javascript
  // 모니터링할 종목 리스트
  const stocks = [
    { code: '005930', name: '삼성전자' },
    { code: '000660', name: 'SK하이닉스' },
    { code: '035420', name: 'NAVER' },
    { code: '051910', name: 'LG화학' },
    { code: '005380', name: '현대차' },
    { code: '006400', name: '삼성SDI' },
    { code: '035720', name: '카카오' },
    { code: '068270', name: '셀트리온' }
  ];

  return stocks.map(stock => ({
    json: {
      stock_code: stock.code,
      stock_name: stock.name
    }
  }));
  ```

#### 📌 Node 4: 백엔드 API 시세 조회
- **노드 타입:** HTTP Request
- **Method:** GET
- **URL:** `http://192.168.50.150:8080/api/market/price/{{$json.stock_code}}`
- **Headers:**
  - `Content-Type`: `application/json`
- **Timeout:** 10000

#### 📌 Node 5: 데이터 변환
- **노드 타입:** Code
- **코드:**
  ```javascript
  const apiResponse = $input.item.json;

  return [{
    json: {
      stock_code: apiResponse.stock_code,
      stock_name: $node["모니터링 종목 설정"].json.stock_name,
      current_price: apiResponse.current_price,
      change_amount: apiResponse.change,
      change_rate: apiResponse.change_rate,
      volume: apiResponse.volume,
      high: apiResponse.high,
      low: apiResponse.low,
      monitored_at: new Date().toISOString()
    }
  }];
  ```

#### 📌 Node 6: Supabase 저장
- **노드 타입:** Supabase
- **Operation:** Insert
- **Table:** `market_monitoring`
- **Credentials:** `auto_stock Supabase` (기존 연결 사용)
- **Columns:**
  - `stock_code`: `={{$json.stock_code}}`
  - `stock_name`: `={{$json.stock_name}}`
  - `current_price`: `={{$json.current_price}}`
  - `change_amount`: `={{$json.change_amount}}`
  - `change_rate`: `={{$json.change_rate}}`
  - `volume`: `={{$json.volume}}`
  - `high`: `={{$json.high}}`
  - `low`: `={{$json.low}}`
  - `monitored_at`: `={{$json.monitored_at}}`
  - `source`: `n8n`

### 2-4. 에러 처리 (선택사항)

#### Node 7: Error Trigger
- API 호출 실패 시 슬랙/이메일 알림 전송

---

## 3. 프론트엔드 확인

### 3-1. 프론트엔드 접속
http://localhost:3000 (또는 배포 URL)

### 3-2. 로그인 후 "실시간 신호" 탭 클릭

### 3-3. 확인 사항
✅ **시장 모니터링 (n8n)** 섹션이 상단에 표시됨
✅ 상승/하락/보합 종목 수 표시
✅ 종목별 현재가, 등락률, 거래량 표시
✅ 1분마다 자동 업데이트
✅ 마지막 업데이트 시간 표시

---

## 4. 문제 해결

### 🔧 데이터가 표시되지 않을 때

#### 1. n8n 워크플로우 확인
```
n8n → Workflows → "시장 모니터링 (1분 주기)"
- Status: Active ✅
- Last Execution: 최근 시간
- Errors: 0
```

#### 2. Supabase 테이블 확인
```sql
-- 최근 데이터 확인
SELECT * FROM market_monitoring
ORDER BY monitored_at DESC
LIMIT 10;
```

#### 3. Realtime 연결 확인
- 브라우저 개발자 도구 Console 확인
- `📊 New market data: ...` 로그 표시 여부

#### 4. 백엔드 API 확인
```bash
curl http://192.168.50.150:8080/api/market/price/005930
```

### ⚠️ 일반적인 문제

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| "워크플로우에서 수집한 데이터가 없습니다" | n8n 워크플로우 비활성화 | n8n에서 Active 전환 |
| 데이터가 오래됨 | 워크플로우 실행 실패 | n8n Executions 탭에서 에러 확인 |
| 특정 종목만 안 나옴 | 종목코드 오류 | n8n 워크플로우에서 종목 리스트 확인 |
| Realtime 업데이트 안 됨 | Supabase Realtime 미활성화 | Supabase Dashboard에서 Realtime 설정 |

### 🔍 디버깅 명령어

```bash
# 1. n8n 워크플로우 실행 로그 확인
docker logs n8n-container -f

# 2. Supabase 연결 테스트
curl -X POST https://hznkyaomtrpzcayayayh.supabase.co/rest/v1/market_monitoring \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"TEST","current_price":100}'

# 3. 백엔드 API 테스트
curl http://192.168.50.150:8080/api/account/status
```

---

## 5. 고급 설정 (선택사항)

### 5-1. 거래량 급증 알림

n8n에 추가 노드:
- 전일 대비 거래량 200% 이상 증가 시 슬랙 알림

### 5-2. 가격 변동 알림

- 등락률 ±5% 이상 시 알림
- 신규 52주 신고가/신저가 시 알림

### 5-3. 데이터 분석

- 일일 평균 거래량 계산
- 변동성 지표 추가
- 시가총액 순위 업데이트

---

## ✅ 체크리스트

설정 완료 후 확인:

- [ ] Supabase `market_monitoring` 테이블 생성
- [ ] Supabase Realtime 활성화
- [ ] n8n 워크플로우 생성 및 Active 전환
- [ ] 프론트엔드에서 시장 모니터링 섹션 확인
- [ ] 1분마다 자동 업데이트 확인
- [ ] 여러 종목 데이터 정상 표시 확인

---

## 📞 지원

문제가 계속되면:
1. n8n Executions 탭에서 에러 로그 확인
2. Supabase Dashboard에서 테이블 데이터 확인
3. 브라우저 개발자 도구 Console 확인

**Happy Trading! 🚀**
