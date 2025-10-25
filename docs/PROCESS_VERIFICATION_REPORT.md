# 자동매매 프로세스 검증 보고서

날짜: 2025-10-26 02:45 KST

## 검증 목적
API 인증 성공을 가정하고, 전체 자동매매 프로세스에 이상이 없는지 검증

---

## 1. update_daily_prices.py 데이터 다운로드 프로세스

### ✅ 정상 작동 확인

**파일:** [backend/update_daily_prices.py](../backend/update_daily_prices.py)

**프로세스:**
1. Kiwoom API 인증 (`_get_access_token()`)
2. 일봉 데이터 조회 (`get_historical_price()`)
   - TR ID: FHKST01010400
   - 파라미터: 종목코드, 조회 기간(일수)
3. 데이터 변환
   - 날짜: YYYYMMDD → YYYY-MM-DD
   - 필드 매핑:
     - `stck_oprc` → open
     - `stck_hgpr` → high
     - `stck_lwpr` → low
     - `stck_clpr` → close
     - `acml_vol` → volume
     - `prdy_ctrt` → change_rate
4. Supabase Upsert
   - 테이블: kw_price_daily
   - 충돌 키: (stock_code, trade_date)
   - 동작: 있으면 업데이트, 없으면 삽입

**검증 결과:**
- ✅ 로직 정상
- ✅ 에러 핸들링 구현됨
- ✅ 여러 종목 일괄 처리 지원 (`--all` 옵션)

**실행 조건:**
- 주식시장 오픈 시간 (월-금 09:00-15:30)에만 API 인증 성공
- 주말/휴일에는 인증 실패 (error 8001)

**실행 명령:**
```bash
# 단일 종목 (60일)
python backend/update_daily_prices.py --stock 005930 --days 60

# 모든 활성 전략 종목
python backend/update_daily_prices.py --all --days 60
```

---

## 2. Backend 지표 계산 API

### ✅ 구현 완료

**파일:** [backend/api/indicators.py](../backend/api/indicators.py)

**API 스펙:**
- **엔드포인트:** POST /api/indicators/calculate
- **요청 본문:**
  ```json
  {
    "stock_code": "005930",
    "indicators": [
      {"name": "ma", "params": {"period": 20}},
      {"name": "ma", "params": {"period": 12}},
      {"name": "bollinger", "params": {"period": 20, "std_dev": 2}},
      {"name": "rsi", "params": {"period": 14}}
    ],
    "days": 60
  }
  ```
- **응답 본문:**
  ```json
  {
    "stock_code": "005930",
    "indicators": {
      "ma_20": 75000,
      "ma_12": 76500,
      "bollinger_upper": 78000,
      "bollinger_middle": 75000,
      "bollinger_lower": 72000,
      "rsi": 45.5,
      "close": 75500
    },
    "calculated_at": "2025-10-26T15:30:00"
  }
  ```

**동작 방식:**
1. DataProvider를 통해 kw_price_daily에서 과거 데이터 조회
2. IndicatorCalculator로 각 지표 계산
   - Supabase indicators 테이블의 formula 사용
   - pandas DataFrame 기반 계산
3. 최신 값 추출 (`.iloc[-1]`)
4. JSON으로 반환

**검증 결과:**
- ✅ API 구현 완료
- ✅ IndicatorCalculator 통합 완료
- ✅ main.py에 라우터 등록 완료
- ⚠️ 충분한 데이터 필요 (MA(20) → 최소 20일, RSI(14) → 최소 14일)

**현재 데이터 상태:**
- kw_price_daily 최신 데이터: 2025-09-12
- 현재 날짜: 2025-10-26
- 데이터 갭: 44일
- 결과: 60일 조회 시 13일치만 반환 → MA(20), Bollinger(20), RSI(14) 모두 NaN

**해결책:**
- 월요일 시장 오픈 시간에 `update_daily_prices.py` 실행
- 최신 60일 데이터 다운로드 → 지표 계산 정상화

---

## 3. n8n Workflow v20 검증

### ❌ **치명적 문제 발견: 기술적 지표가 계산되지 않음**

**파일:**
- [n8n-workflows/auto-trading-with-capital-validation-v20.json](../n8n-workflows/auto-trading-with-capital-validation-v20.json)
- [n8n-workflows/n8n_signal_generation_code_with_stock_metadata.js](../n8n-workflows/n8n_signal_generation_code_with_stock_metadata.js)

**현재 워크플로우 흐름:**
1. ✅ 5분마다 실행 (스케줄 트리거)
2. ✅ 환경변수 설정 (SUPABASE_URL, BACKEND_URL 등)
3. ✅ 장시간 체크 (월-금 09:00-15:30)
4. ✅ Kiwoom API 인증
5. ✅ 활성 전략 조회 (Supabase strategies 테이블)
6. ✅ 종목 코드 추출
7. ✅ Kiwoom 호가 조회 (각 종목별)
8. ✅ 데이터 병합
9. ❌ **조건 체크 및 신호 생성** ← **문제 지점**
10. ✅ 신호 저장 (trading_signals 테이블)
11. ✅ 매수 신호시 주문 실행

**문제 상세:**

[n8n_signal_generation_code_with_stock_metadata.js:55-60](../n8n-workflows/n8n_signal_generation_code_with_stock_metadata.js#L55)
```javascript
const indicators = {
  close: estimatedPrice,      // ✅ 종가 (호가 평균)
  sel_price: selPrice,         // ✅ 매도호가
  buy_price: buyPrice,         // ✅ 매수호가
  volume: selVolume + buyVolume // ✅ 거래량
};
// ❌ ma_20, ma_12, bollinger_*, rsi 등이 없음!
```

**전략 조건 (strategies 테이블):**
```json
{
  "buy": [
    {"left": "close", "operator": "<", "right": "ma_20"},
    {"left": "close", "operator": "<", "right": "ma_12"}
  ]
}
```

**조건 평가 로직:**
```javascript
const left = indicators[condition.left] || 0;  // close = 75500
const right = indicators[condition.right];      // ma_20 = undefined ❌
// undefined와 비교 → 항상 false
```

**결과:**
- `indicators["ma_20"]` = `undefined`
- `indicators["ma_12"]` = `undefined`
- 매수 조건이 항상 `false`로 평가됨
- **매수 신호가 절대 발생하지 않음**

### **이것이 "몇일동안 한번도 매수신호가 나타나지 않은" 근본 원인입니다!**

---

## 4. 전체 프로세스 문제 요약

| 구성요소 | 상태 | 비고 |
|---------|------|------|
| Kiwoom API 인증 | ✅ | 시장 오픈 시간에만 작동 |
| update_daily_prices.py | ✅ | 로직 정상 |
| kw_price_daily 데이터 | ⚠️ | 최신 데이터 2025-09-12 (44일 갭) |
| Backend indicators API | ✅ | 구현 완료, 데이터 부족으로 NaN 반환 |
| indicators 테이블 | ✅ | 17개 활성 지표, formula 정상 |
| indicator_columns 테이블 | ✅ | 컬럼 매핑 정상 |
| strategies 테이블 | ✅ | 조건 수정 완료 (ma_20, ma_12) |
| **n8n workflow v20** | ❌ | **지표 계산 누락** |

---

## 5. 해결 방안

### 단기 해결 (필수):

#### A. 최신 데이터 다운로드
**시기:** 월요일 09:00-15:30 (시장 오픈 시간)
```bash
python backend/update_daily_prices.py --all --days 60
```

#### B. n8n Workflow v21 생성

**추가할 노드:** "지표 계산 API 호출" (HTTP Request)
- **위치:** "키움 호가 조회" 노드와 "조건 체크 및 신호 생성" 노드 사이
- **Method:** POST
- **URL:** `{{ $('환경변수 설정').item.json.BACKEND_URL }}/api/indicators/calculate`
- **Body:**
  ```json
  {
    "stock_code": "{{ $json.stock_code }}",
    "indicators": [
      {"name": "ma", "params": {"period": 20}},
      {"name": "ma", "params": {"period": 12}},
      {"name": "bollinger", "params": {"period": 20}},
      {"name": "rsi", "params": {"period": 14}}
    ],
    "days": 60
  }
  ```

**수정할 코드:** "조건 체크 및 신호 생성" 노드
```javascript
// 기존 indicators 객체
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume
};

// ⭐ Backend API 결과 병합
const backendIndicators = $('지표 계산 API 호출').item.json.indicators || {};
Object.assign(indicators, backendIndicators);

// 이제 indicators = {
//   close: 75500,
//   ma_20: 75000,
//   ma_12: 76500,
//   bollinger_upper: 78000,
//   ...
// }
```

### 장기 개선 (선택):

1. **캐싱 구현**
   - 같은 종목의 지표를 5분마다 재계산하지 않고, 캐시 사용
   - Redis 또는 메모리 캐시

2. **공휴일 필터링**
   - 한국 주식시장 공휴일 데이터 통합
   - 불필요한 API 호출 방지

3. **지표 계산 최적화**
   - Batch 처리: 105개 종목을 한 번에 계산
   - 병렬 처리: multiprocessing 활용

---

## 6. 테스트 계획

### 월요일 시장 오픈 후:

1. **데이터 다운로드 (09:00-09:10)**
   ```bash
   python backend/update_daily_prices.py --stock 005930 --days 60
   ```
   - 예상 결과: 60일치 데이터 Upsert 성공

2. **지표 계산 API 테스트 (09:10-09:15)**
   ```bash
   python backend/test_full_indicator_flow.py
   ```
   - 예상 결과: MA(20), MA(12), Bollinger, RSI 모두 정상 값 반환

3. **n8n Workflow v21 배포 (09:15-09:20)**
   - v20 비활성화
   - v21 활성화
   - 첫 실행 대기 (최대 5분)

4. **매수 신호 모니터링 (09:20-15:30)**
   - trading_signals 테이블 확인
   - buy_signal = true인 레코드 발생 확인
   - MarketMonitor UI에서 실시간 신호 확인

---

## 7. 결론

### 문제의 근본 원인:
**n8n workflow v20이 Backend 지표 계산 API를 호출하지 않아**, `ma_20`, `ma_12` 등의 지표 값이 `undefined`가 되고, 전략 조건이 항상 `false`로 평가되어 **매수 신호가 절대 발생하지 않았습니다.**

### 다음 단계:
1. ✅ 문제 식별 완료
2. ⏳ 월요일 시장 오픈 대기
3. ⏳ 데이터 다운로드 실행
4. ⏳ n8n workflow v21 생성 및 배포
5. ⏳ 매수 신호 발생 확인

---

## 8. 참고 문서

- [AUTO_TRADING_BUY_PROCESS.md](./AUTO_TRADING_BUY_PROCESS.md) - 자동매매 프로세스 전체 문서
- [INDICATOR_CALCULATION_STATUS.md](./INDICATOR_CALCULATION_STATUS.md) - 지표 계산 검증 결과
- [fix_indicator_columns.sql](../supabase/fix_indicator_columns.sql) - indicator_columns 테이블 수정
- [fix_indicators_table.sql](../supabase/fix_indicators_table.sql) - indicators 테이블 수정
- [fix_strategy_conditions.sql](../supabase/fix_strategy_conditions.sql) - 전략 조건 수정
