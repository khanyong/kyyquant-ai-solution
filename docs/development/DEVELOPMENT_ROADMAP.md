# KyyQuant AI Solution - Development Roadmap

## 📊 전체 프로젝트 진행률: 78% ███████████████░░░

### 🎯 핵심 모듈별 진행 상황

| 모듈 | 진행률 | 상태 | 설명 |
|------|--------|------|------|
| 📈 **투자 유니버스 필터링** | 95% | 🟢 운영중 | 섹터 데이터만 미구현 |
| 🤖 **자동매매 시스템** | 75% | 🟡 개발중 | n8n 워크플로우 통합 필요 |
| 📊 **백테스팅 엔진** | 60% | 🟡 개발중 | 기본 기능 완료, 고급 기능 개발 중 |
| 🎯 **전략 빌더** | 95% | 🟢 운영중 | 3단계 전략 시스템 구현 완료 |
| 📱 **실시간 모니터링** | 70% | 🟡 개발중 | WebSocket → Supabase Realtime 전환 |
| 🔐 **사용자 인증** | 90% | 🟢 운영중 | Supabase Auth 통합 완료 |
| 💾 **데이터 파이프라인** | 95% | 🟢 운영중 | 키움 REST API 토큰 발급, pykrx 실시간 데이터 |
| 🎨 **UI/UX** | 80% | 🟢 운영중 | Material-UI v5 통합 완료 |

---

## 📅 최근 업데이트 (2025-09-13) - 상세 내역

### 🔥 0. 키움 REST API & 실시간 데이터 파이프라인 구축 [100% 완료] - NEW!

#### 0.1 키움증권 REST API 인증 시스템 구현
- **API 토큰 발급 성공** ✅
  - 2024년 3월 출시된 키움 REST API 연동
  - 모의투자 환경 설정 (`https://mockapi.kiwoom.com`)
  - OAuth2 인증 방식 구현
  - 파라미터 형식 수정: `appsecret` → `secretkey`

- **문제 해결 과정** ✅
  ```python
  # 잘못된 형식 (기존)
  token_data = {
      "grant_type": "client_credentials",
      "appkey": app_key,
      "appsecret": app_secret  # ❌ 오류
  }

  # 올바른 형식 (수정)
  token_data = {
      "grant_type": "client_credentials",
      "appkey": app_key,
      "secretkey": app_secret  # ✅ 정상
  }
  ```

#### 0.2 NAS REST API Bridge Server 구축
- **Synology NAS 서버 배포** ✅
  - Docker 컨테이너로 FastAPI 서버 운영
  - IP: `192.168.50.150:8080`
  - Supabase 연동 완료
  - 2,878개 전체 종목 관리

- **아키텍처 구성** ✅
  ```yaml
  NAS Server (Docker):
    - FastAPI 2.0.0
    - Python 3.9
    - pykrx 1.0.45  # 실시간 시세
    - supabase 2.0.2
    - requests 2.31.0

  Data Flow:
    KRX → pykrx → NAS API → Supabase → Frontend
  ```

#### 0.3 전체 종목 데이터 수집 시스템
- **종목 메타데이터 수집** ✅
  - `fetch_all_stocks_batch.py` 구현
  - 전체 2,878개 종목 수집 완료
    - KOSPI: 959개
    - KOSDAQ: 1,803개
    - KONEX: 116개
  - `stock_metadata` 테이블 구축

- **실시간 가격 데이터 수집** ✅
  - `download_all_stocks_data.py` 구현
  - pykrx 라이브러리 활용 (한국거래소 데이터)
  - 배치 처리: 종목당 0.7초
  - 전체 처리 시간: 약 33분

#### 0.4 데이터베이스 최적화
- **Supabase RLS 정책 수정** ✅
  ```sql
  -- RLS 정책 문제 해결
  CREATE POLICY "Allow all users to manage stock_metadata"
  ON stock_metadata FOR ALL
  USING (true)
  WITH CHECK (true);
  ```

- **페이지네이션 구현** ✅
  - 1,000개 제한 우회 로직
  - limit/offset 방식 적용
  - 500개씩 배치 처리

#### 0.5 키움 API 시세 조회 이슈 및 대안
- **문제점** ⚠️
  - 시세 조회 API 500 Internal Server Error
  - `/uapi/domestic-stock/v1/quotations/inquire-price` 오류
  - 키움 REST API 초기 버전 불안정성

- **해결 방안** ✅
  - 토큰 발급: 키움 REST API 사용
  - 시세 데이터: pykrx 라이브러리 사용 (임시)
  - 향후 키움 API 안정화 시 전환 예정

#### 0.6 구현된 주요 파일
| 파일명 | 설명 | 상태 |
|--------|------|------|
| `backend/test_kiwoom_direct.py` | 키움 API 연동 테스트 | ✅ 완료 |
| `backend/kiwoom_bridge/main.py` | NAS API 서버 메인 | ✅ 완료 |
| `backend/fetch_all_stocks_batch.py` | 전체 종목 수집 | ✅ 완료 |
| `backend/download_all_stocks_data.py` | 실시간 가격 수집 | ✅ 완료 |
| `backend/kiwoom_bridge/requirements.txt` | 의존성 관리 | ✅ 완료 |
| `backend/kiwoom_bridge/.env` | 환경 변수 설정 | ✅ 완료 |

### ✅ 1. 투자 유니버스 필터링 시스템 [95% 완료]

#### 1.1 데이터 수집 및 저장 시스템
- **Kiwoom OpenAPI 통합** ✅
  - `backend/collect_all_stocks.py` - 전체 종목 수집 엔진
  - 3,349개 한국 주식 데이터 수집 성공 (KOSPI 2,031개 + KOSDAQ 1,318개)
  - ETF, SPAC, REIT 자동 필터링 로직 구현
  - 32-bit Python 3.7 환경 구성 (Kiwoom API 호환성)

- **데이터베이스 구조 설계** ✅
  - Supabase PostgreSQL 활용
  - `kw_financial_snapshot` 테이블 - 시계열 재무 데이터
  - `kw_stock_list` 테이블 - 종목 마스터 정보
  - `kw_collection_log` 테이블 - 수집 이력 관리
  - 인덱싱 최적화 (stock_code, snapshot_date, market_cap)

- **인코딩 문제 해결** ✅
  - `backend/fix_all_broken_names.py` - 한글 인코딩 수정 스크립트
  - CP949 → UTF-8 변환 처리
  - Latin-1 잘못된 인코딩 복구
  - 21개 종목 수동 매핑 테이블 구성

- **데이터 정합성 관리** ✅
  - 중복 레코드 자동 제거 (8,243개 → 3,349개)
  - UNIQUE 제약조건 추가 (stock_code + snapshot_date)
  - 트랜잭션 기반 배치 처리

#### 1.2 실시간 필터링 UI 구현
- **메인 필터링 컴포넌트** ✅
  - `TradingSettingsWithUniverse.tsx` (1,100+ lines)
  - 3단계 누적 필터링 시스템
  - 실시간 통계 업데이트
  - 시각적 필터링 플로우 다이어그램

- **필터링 기능 상세** ✅
  ```typescript
  // 구현된 필터 체인
  전체 종목 (3,349개)
    ↓ 가치평가 필터 (시가총액, PER, PBR)
    ↓ 재무지표 필터 (ROE, 부채비율)
    ↓ 섹터 필터 (24개 업종) - 데이터 미구현
    → 최종 투자 유니버스
  ```

- **종목 리스트 뷰어** ✅
  - `InvestmentUniverse.tsx` - 전체 종목 테이블 뷰
  - 페이지네이션 구현 (25/50/100개씩 보기)
  - 실시간 검색 및 정렬
  - Excel 다운로드 기능 (예정)

#### 1.3 페이지네이션 및 대용량 데이터 처리
- **Supabase 페이지네이션 해결** ✅
  ```typescript
  // 1,000개 제한 우회 - 다중 페이지 로드
  while (offset < finalTotalCount) {
    const { data } = await supabase
      .from('kw_financial_snapshot')
      .select('*')
      .range(offset, offset + pageSize - 1)
    allData = [...allData, ...pageData]
    offset += pageSize
  }
  ```
- 최대 10,000개 종목 로드 지원
- 메모리 최적화 및 가상 스크롤링 (예정)

### ✅ 2. 누적 필터링 로직 구현 [100% 완료]

#### 2.1 필터 상태 관리 시스템
- **State 구조 개선** ✅
  ```typescript
  // 필터 적용 상태
  appliedFilters: { valuation, financial, sector }
  // 필터 값 저장
  currentFilterValues: { valuation: {...}, financial: {...} }
  // 누적 필터링 결과
  cumulativeFilteredStocks: Stock[]
  // 필터링 통계
  filterStats: { total, afterMarketCap, afterFinancial, final }
  ```

#### 2.2 필터 적용 로직 개선
- **문제점 해결** ✅
  1. 전체 종목 수 리셋 문제 (3,349 → 1,000) ✅ 해결
  2. 가치평가 필터 리셋 문제 (54개 → 3,349개) ✅ 해결
  3. 재무지표 재적용 시 누적 미유지 (54개 → 1,077개) ✅ 해결
  4. 필터 체인 끊김 현상 ✅ 해결

- **핵심 개선 코드** ✅
  ```typescript
  // 필터 재적용 시 이전 필터 값 사용
  if (appliedFilters.valuation && currentFilterValues.valuation) {
    const valuationFilters = currentFilterValues.valuation
    filteredData = applyValuationFilter(allStocks, valuationFilters)
    // 이제 재무지표 필터를 적용
    filteredData = applyFinancialFilter(filteredData, financialFilters)
  }
  ```

### ✅ 3. UI/UX 대규모 개선 [85% 완료]

#### 3.1 컴포넌트 구조 최적화
- **중복 제거** ✅
  - `TestInvestmentUniverse` 컴포넌트 제거
  - 필터 UI 중복 제거 (상단 설정과 하단 리스트 분리)
  - 불필요한 스크롤바 제거

- **레이아웃 개선** ✅
  - 65:35 비율의 투자설정/유니버스 분할 뷰
  - 반응형 디자인 적용
  - Material-UI v5 다크 테마 최적화

#### 3.2 사용자 경험 개선
- **필터 초기화 버튼** ✅
  - 모든 필터 및 값 일괄 초기화
  - 애니메이션 효과 추가

- **실시간 피드백** ✅
  - 필터 적용 진행률 표시
  - 로딩 인디케이터
  - 필터별 통과율 표시

- **시각적 개선** ✅
  - 필터링 플로우 다이어그램
  - 색상 코딩된 필터 상태
  - 뱃지형 카운터 표시

### ✅ 4. 3단계 전략 빌더 시스템 [100% 완료] - 2025.09.05

#### 4.1 아키텍처 설계
- **StageBasedStrategy 컴포넌트** ✅
  - 매수/매도 각각 독립된 3단계 평가 시스템
  - 단계별 최대 5개 지표 동시 설정 가능
  - 총 30개 조건 조합 가능 (매수 15개 + 매도 15개)

#### 4.2 단계별 전략 구성
- **1단계: 기본 필터링** ✅
  - 시장 전반 상태 평가
  - 섹터/업종 조건
  - 거래량/유동성 필터
  - 기본 추세 확인

- **2단계: 신호 강화** ✅
  - 모멘텀 지표 확인
  - 추세 강도 평가
  - 보조지표 크로스오버
  - 다이버전스 확인

- **3단계: 최종 확인** ✅
  - 진입 타이밍 정밀 조정
  - 리스크 체크
  - 최종 필터링
  - 포지션 사이즈 결정

#### 4.3 고급 기능
- **투자 흐름 관리 (InvestmentFlowManager)** ✅
  - 필터 우선 방식: 유니버스 필터링 → 전략 적용
  - 전략 우선 방식: 전략 신호 → 유니버스 확인
  - 혼합 방식: 동시 평가

- **전략 저장/불러오기** ✅
  - Supabase strategies 테이블 연동
  - JSON 형식 전략 export/import
  - 버전 관리 시스템
  - 전략 공유 기능

#### 4.4 UI/UX 개선
- **토글 스위치** ✅
  - 3단계 시스템 ↔ 기본 시스템 전환
  - 실시간 미리보기
  - 드래그 앤 드롭 지표 배치

- **시각적 피드백** ✅
  - 단계별 진행 상태 표시
  - 조건 충족 여부 실시간 표시
  - 백테스트 연동 버튼

### 🔧 5. 기술 스택 상세 [90% 구축]

#### Backend 스택
```yaml
Runtime:
  - Python: 3.7.9 (32-bit) # Kiwoom API 필수
  - Node.js: 18.x # n8n 워크플로우

Libraries:
  - pykiwoom: 0.4.2 # Kiwoom OpenAPI 래퍼
  - supabase: 2.x # Supabase Python Client
  - pandas: 1.3.x # 데이터 처리
  - schedule: 1.x # 스케줄링

APIs:
  - Kiwoom OpenAPI # 실시간 시세, 주문
  - Supabase REST API # 데이터베이스
  - n8n Webhook # 자동매매 트리거
```

#### Frontend 스택
```yaml
Framework:
  - React: 18.2.0
  - TypeScript: 5.x
  - Vite: 5.x # 빌드 도구

UI/UX:
  - Material-UI: 5.x
  - Emotion: 11.x # CSS-in-JS
  - Recharts: 2.x # 차트

State & Data:
  - Redux Toolkit: 2.x
  - RTK Query: 2.x
  - Supabase JS: 2.x

Deployment:
  - Vercel # 프론트엔드 호스팅
  - GitHub Actions # CI/CD
```

### 📊 5. 데이터베이스 스키마 상세

#### 5.1 핵심 테이블 구조
```sql
-- 재무 스냅샷 테이블 (시계열 데이터)
CREATE TABLE kw_financial_snapshot (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    market VARCHAR(20) CHECK (market IN ('KOSPI', 'KOSDAQ')),
    snapshot_date DATE NOT NULL,
    snapshot_time TIME,
    
    -- 시가총액 정보
    market_cap BIGINT,              -- 시가총액 (원)
    shares_outstanding BIGINT,       -- 발행주식수
    
    -- 가치평가 지표
    per DECIMAL(10,2),              -- PER (배)
    pbr DECIMAL(10,2),              -- PBR (배)
    eps INTEGER,                    -- EPS (원)
    bps INTEGER,                    -- BPS (원)
    
    -- 수익성 지표
    roe DECIMAL(10,2),              -- ROE (%)
    roa DECIMAL(10,2),              -- ROA (%) - 미구현
    
    -- 안정성 지표
    debt_ratio DECIMAL(10,2),       -- 부채비율 (%) - 미구현
    current_ratio DECIMAL(10,2),    -- 유동비율 (%) - 미구현
    
    -- 가격 정보
    current_price INTEGER,           -- 현재가
    change_rate DECIMAL(5,2),       -- 등락률
    high_52w INTEGER,               -- 52주 최고가
    low_52w INTEGER,                -- 52주 최저가
    
    -- 거래 정보
    volume BIGINT,                  -- 거래량
    trading_value BIGINT,           -- 거래대금
    foreign_ratio DECIMAL(5,2),     -- 외국인 보유율
    
    -- 섹터 정보 (현재 NULL)
    sector VARCHAR(50),             -- 업종 분류
    industry VARCHAR(100),          -- 세부 산업
    
    -- 메타 정보
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 복합 유니크 키
    UNIQUE(stock_code, snapshot_date)
);

-- 인덱스 최적화
CREATE INDEX idx_kw_snapshot_lookup 
ON kw_financial_snapshot(stock_code, snapshot_date DESC);

CREATE INDEX idx_kw_snapshot_filter 
ON kw_financial_snapshot(market_cap DESC, per, pbr, roe);

CREATE INDEX idx_kw_snapshot_sector 
ON kw_financial_snapshot(sector, market_cap DESC)
WHERE sector IS NOT NULL;
```

### 🐛 6. 버그 수정 상세 내역

#### 6.1 한글 인코딩 문제 [100% 해결]
```python
# 문제: ¿µ¸²¿ø¼ÒÇÁÆ®·¦ 같은 깨진 텍스트
# 원인: Kiwoom API의 CP949 인코딩을 Latin-1로 잘못 해석
# 해결:
def fix_encoding(broken_text):
    try:
        return broken_text.encode('latin-1').decode('cp949')
    except:
        return manual_mapping.get(broken_text, broken_text)
```

#### 6.2 페이지네이션 문제 [100% 해결]
```typescript
// 문제: Supabase 1,000개 제한
// 해결: 다중 페이지 순차 로드
const loadAllData = async () => {
  let allData = []
  let offset = 0
  const pageSize = 1000
  
  while (offset < totalCount) {
    const { data } = await supabase
      .from('table')
      .select('*')
      .range(offset, offset + pageSize - 1)
    allData = [...allData, ...data]
    offset += pageSize
    
    if (offset >= 10000) break // 최대 10,000개 제한
  }
  return allData
}
```

#### 6.3 필터 리셋 문제 [100% 해결]
```typescript
// 문제: 재무지표 필터 적용 시 가치평가 필터 리셋
// 원인: 필터 체인 미구현
// 해결: currentFilterValues로 이전 필터 저장 및 재적용
const handleFilterApplication = (filterType, filters) => {
  // 필터 값 저장
  setCurrentFilterValues(prev => ({ ...prev, [filterType]: filters }))
  
  // 누적 필터링
  let filteredData = [...allStocks]
  
  // 이전 필터들 재적용
  if (appliedFilters.valuation && currentFilterValues.valuation) {
    filteredData = applyValuationFilter(filteredData, currentFilterValues.valuation)
  }
  
  // 현재 필터 적용
  filteredData = applyCurrentFilter(filteredData, filters)
}
```

### 📝 7. 주요 파일 변경 내역 (상세)

#### Backend 파일
| 파일명 | 변경 내용 | 코드 라인 | 상태 |
|--------|-----------|-----------|------|
| `collect_all_stocks.py` | 전체 종목 수집 로직 | 450+ | ✅ 완료 |
| `fix_all_broken_names.py` | 인코딩 수정 스크립트 | 200+ | ✅ 완료 |
| `download_all_kiwoom_data.py` | 재무 데이터 다운로드 | 350+ | ✅ 완료 |
| `setup_complete_database.py` | DB 초기화 스크립트 | 150+ | ✅ 완료 |
| `kiwoom_real_api.py` | 실시간 시세 API | 300+ | 🟡 개발중 |
| `backtest_with_supabase.py` | 백테스팅 엔진 | 400+ | 🟡 개발중 |

#### Frontend 파일
| 파일명 | 변경 내용 | 코드 라인 | 상태 |
|--------|-----------|-----------|------|
| `TradingSettingsWithUniverse.tsx` | 메인 필터링 UI | 1,100+ | ✅ 완료 |
| `InvestmentUniverse.tsx` | 종목 리스트 뷰어 | 395+ | ✅ 완료 |
| `TradingSettingsSimplified.tsx` | 투자 설정 UI | 500+ | ✅ 완료 |
| `StrategyBuilder.tsx` | 전략 빌더 | 600+ | ✅ 완료 |
| `BacktestResults.tsx` | 백테스트 결과 | 400+ | 🟡 개발중 |
| `AutoTradingPanel.tsx` | 자동매매 패널 | 350+ | 🟡 개발중 |

#### 데이터베이스 파일
| 파일명 | 변경 내용 | 상태 |
|--------|-----------|------|
| `create_kw_financial_snapshot.sql` | 재무 스냅샷 테이블 | ✅ 완료 |
| `create_all_kiwoom_tables.sql` | 전체 테이블 생성 | ✅ 완료 |
| `migrate_to_kw_tables.sql` | 데이터 마이그레이션 | ✅ 완료 |
| `create_indexes.sql` | 인덱스 최적화 | ✅ 완료 |

## 🚀 향후 로드맵 (우선순위별)

### 🔴 긴급 (1주일 내)
1. **섹터 데이터 수집** [0%]
   - Kiwoom GetUpjongCode() API 활용
   - 24개 업종 분류 매핑
   - NULL 값 업데이트

2. **필터링 성능 최적화** [20%]
   - 가상 스크롤링 구현
   - 메모이제이션 적용
   - 디바운싱 처리

### 🟡 단기 (1개월 내)
1. **자동 데이터 수집** [30%]
   - Windows Task Scheduler 설정
   - 일일 수집 스크립트
   - 에러 알림 시스템

2. **백테스팅 통합** [40%]
   - 필터링된 유니버스 연동
   - 성과 지표 계산
   - 리포트 생성

3. **n8n 워크플로우 연동** [50%]
   - Webhook 트리거 설정
   - 주문 실행 API
   - 리스크 관리

### 🟢 중기 (3개월 내)
1. **고급 필터 기능** [10%]
   - 기술적 지표 (RSI, MACD, 볼린저밴드)
   - 펀더멘털 스코어링
   - AI 기반 필터 추천

2. **포트폴리오 최적화** [5%]
   - 마코위츠 모델
   - 리스크 패리티
   - 켈리 공식

3. **실시간 알림** [15%]
   - 가격 알림
   - 신호 알림
   - 주문 체결 알림

### 🔵 장기 (6개월 내)
1. **멀티 마켓 지원** [0%]
   - 미국 주식 (IB API)
   - 암호화폐 (Binance API)
   - 선물/옵션

2. **머신러닝 통합** [0%]
   - 가격 예측 모델
   - 패턴 인식
   - 감성 분석

3. **모바일 앱** [0%]
   - React Native
   - 실시간 모니터링
   - 원터치 주문

## 📚 참고 문서
- [투자 데이터 수집 가이드](./INVESTMENT_DATA_COLLECTION_GUIDE.md)
- [백테스팅 가이드](./BACKTEST_GUIDE.md)
- [전략 워크플로우](./STRATEGY_WORKFLOW.md)
- [Kiwoom API 설정](./KIWOOM_API_SETUP.md)
- [n8n 워크플로우 설정](./n8n-workflows/SETUP_GUIDE.md)

## 🔄 업데이트 이력
- **2025-09-13 18:00**: 키움 REST API 토큰 발급 성공, pykrx 실시간 데이터 연동
- **2025-09-13 16:00**: NAS REST API Bridge Server 구축 완료
- **2025-09-13 14:00**: 전체 2,878개 종목 메타데이터 수집 완료
- **2025-09-13 12:00**: Supabase RLS 정책 수정, 페이지네이션 구현
- **2025-09-06 15:30**: 투자 유니버스 필터링 누적 로직 완성
- **2025-09-06 14:00**: 필터 리셋 버그 수정
- **2025-09-06 12:00**: 페이지네이션 문제 해결
- **2025-09-06 10:00**: 한글 인코딩 문제 해결
- **2025-09-05**: Supabase 데이터 파이프라인 구축
- **2025-09-04**: n8n 자동매매 시스템 초기 구축
- **2025-09-03**: Material-UI v5 마이그레이션
- **2025-09-02**: React 18 업그레이드

## 💡 기술 부채 및 개선 사항
1. **코드 리팩토링 필요**
   - `TradingSettingsWithUniverse.tsx` 1,100라인 → 컴포넌트 분리 필요
   - 중복 코드 제거 (DRY 원칙)
   - 타입 정의 강화

2. **테스트 커버리지**
   - 현재 0% → 목표 80%
   - Jest + React Testing Library 설정
   - E2E 테스트 (Cypress)

3. **문서화**
   - API 문서 (Swagger)
   - 컴포넌트 문서 (Storybook)
   - 사용자 가이드

4. **성능 모니터링**
   - Sentry 에러 트래킹
   - Google Analytics
   - 성능 메트릭스

---

*Last Updated: 2025-09-13 18:00*
*Total Project Size: ~28,000 lines of code*
*Active Contributors: 1*
*Version: 0.9.0-beta*