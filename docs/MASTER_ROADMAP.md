# 🚀 KyyQuant AI Solution - 마스터 로드맵

> **프로젝트 전체 계획 및 진행 상황 통합 문서**
>
> **최종 업데이트**: 2025-10-20
> **전체 진행률**: 80.8% (21개 완료 / 26개 작업)
> **현재 단계**: n8n 워크플로우 모니터링 완료 → 자동매매 연동 준비 중

---

## 📊 전체 프로젝트 현황

### ✅ 완료된 핵심 마일스톤

| 마일스톤 | 진행률 | 완료일 | 핵심 성과 |
|---------|--------|--------|-----------|
| **Phase 1: 기본 시스템** | 100% | 2024-09 | React 18 + Supabase 인프라 구축 |
| **Phase 2: 전략 시스템** | 100% | 2025-01 | 전략 빌더, 백테스트, 템플릿 시스템 |
| **Phase 2.5a: 표준화** | 100% | 2025-10-01 | 지표 표준화, 프리플라이트 검증, 자동 변환 |
| **Phase 2.5b: 데이터 재현성** | 0% | 진행 예정 | dataset_id, 해시 기반 버전 관리 |
| **Phase 3: API/워커 분리** | 0% | 계획 중 | Redis 작업 큐, 비동기 백테스트 |

### 🎯 진행 중인 작업

| 작업 | 상태 | 우선순위 | 예상 완료 |
|------|------|----------|-----------|
| NAS 서버 배포 | 준비 완료 | 🔴 긴급 | 2025-10-02 |
| Supabase 템플릿 재생성 | 준비 완료 | 🔴 긴급 | 2025-10-02 |
| Phase 2.5b 구현 | 설계 완료 | 🟡 단기 | 2025-10-05 |
| n8n 워크플로우 연동 | 완료 | ✅ 완료 | 2025-10-20 |

---

## 📋 작업 목록 (Task 1-26)

### ✅ Task 1-19: 완료된 작업 (2024.08 - 2025.01)

<details>
<summary><b>Task 1: 프로젝트 초기 설정</b> [완료: 2024-08-26]</summary>

- React 18 + Vite + TypeScript 환경 구성
- Material-UI v5 다크 테마 설정
- Redux Toolkit 상태관리
- React Router v6 라우팅
- ESLint, Prettier 코드 품질 도구
</details>

<details>
<summary><b>Task 2: 데이터베이스 스키마 설계</b> [완료: 2024-08-28]</summary>

- Supabase PostgreSQL 15 설계
- 사용자 관리 테이블 (profiles, roles, permissions)
- 전략 관리 테이블 (strategies, conditions, indicators)
- 백테스트 결과 테이블 (results, trades, daily_returns)
- 게시판 시스템 (boards, posts, comments)
- Row Level Security (RLS) 정책 구현
</details>

<details>
<summary><b>Task 3: Supabase 인증 시스템</b> [완료: 2024-08-31]</summary>

- Supabase Auth 연동
- 이메일/비밀번호 로그인
- Google/GitHub OAuth 2.0
- JWT 토큰 관리, 세션 자동 갱신
- RBAC 권한 시스템 (admin, user, premium, vip)
</details>

<details>
<summary><b>Task 4: 전략 빌더 시스템</b> [완료: 2024-08-30]</summary>

- 10개 기술적 지표 구현 (RSI, MACD, 볼린저밴드, SMA, EMA, Stochastic, CCI, ADX, OBV, ATR)
- AND/OR 로직 게이트 조건 설정
- 일목균형표 특수 조건 (구름대 돌파, 삼역전환)
- **3단계 전략 시스템** (2025-09-05 추가)
  - 매수/매도 각 3단계 독립 평가
  - 단계별 최대 5개 지표 설정
  - 필터 우선/전략 우선 선택
- 리스크 관리 (손절, 익절, 트레일링 스톱)
- 전략 저장/관리 (Supabase, JSON export)
</details>

<details>
<summary><b>Task 5: 백테스팅 시스템</b> [완료: 2024-08-30]</summary>

- 틱 데이터 시뮬레이션 엔진
- 슬리피지 및 수수료 반영
- 성과 분석 차트 (Chart.js)
- 리스크 분석 (샤프 지수, 소르티노, MDD, VaR)
- 거래 분석 (승률, 손익비, 평균 보유기간)
- 섹터별 성과 분석
</details>

<details>
<summary><b>Task 6: 커뮤니티 게시판</b> [완료: 2024-08-30]</summary>

- 8개 게시판 (공지사항, 자유, Q&A, 전략 공유, 시장 분석 등)
- WYSIWYG 에디터, 이미지/파일 첨부
- 댓글/대댓글 시스템
- 좋아요/조회수/북마크
- 게시판별 권한 관리
</details>

<details>
<summary><b>Task 7: 투자 설정 시스템</b> [완료: 2024-08-30]</summary>

- 투자 유니버스 설정 (시가총액, PER, PBR, ROE, 부채비율)
- 포트폴리오 관리 (종목 수, 비중 제한, 리밸런싱 주기)
- 매매 조건 설정 (진입/청산, 분할 매수/매도)
- 위험 관리 (계좌/일일 손실 한도, 변동성 기반 조절)
- 업종/테마 설정
</details>

<details>
<summary><b>Task 8: 실시간 대시보드</b> [완료: 2024-09-03]</summary>

- 시장 개요 위젯 (KOSPI/KOSDAQ 지수, 업종 지수)
- 포트폴리오 현황 (보유 종목, 평가 손익, 수익률 차트)
- 실시간 시세 WebSocket → **Supabase Realtime 전환 예정**
- 실시간 차트 (TradingView 통합)
- 주문 패널 (원클릭 주문, 예약 주문)
</details>

<details>
<summary><b>Task 9: 자동매매 시스템</b> [완료: 2024-09-03]</summary>

- 자동매매 UI (전략 선택, ON/OFF, 모니터링)
- 전략 실행 컨트롤 (시작/중지/긴급정지)
- **키움 API 서버** (Python FastAPI, COM 객체 관리)
- 실시간 주문 실행 (신호 발생 시 자동 주문)
- 포지션 모니터링 (실시간 손익, 리스크 지표)
</details>

<details>
<summary><b>Task 10: Supabase 데이터 파이프라인</b> [완료: 2024-09-03]</summary>

- positions, account_balance 테이블 재구성
- 7단계 데이터 파이프라인 (market_data → indicators → signals → orders → positions)
- backend 폴더 구조 정리 (api/, core/, database/, scripts/, sql/)
- RLS 정책 수정 및 테스트
</details>

<details>
<summary><b>Task 11: n8n 워크플로우 시스템</b> [완료: 2024-09-03]</summary>

- n8n 연동 시스템 (n8n_connector.py, n8n_config.py)
- Supabase 모니터링 워크플로우 (1분마다 활성 전략 체크)
- 자동매매 스케줄러 (APScheduler, 장 시간 09:00-15:30)
- **실제 구현은 Task #20에서 진행 중**
</details>

<details>
<summary><b>Task 12: 시스템 아키텍처 문서화</b> [완료: 2024-09-03]</summary>

- SYSTEM_ARCHITECTURE.md (시스템 구성, 데이터 흐름, 6단계 프로세스)
- backend/README.md (폴더 구조, 모듈 역할)
</details>

<details>
<summary><b>Task 13: 투자 유니버스 필터링</b> [완료: 2025-09-06]</summary>

- **3,349개 한국 주식 데이터 수집** (KOSPI 2,031 + KOSDAQ 1,318)
- 키움 OpenAPI 연동 (32-bit Python 3.7)
- 한글 인코딩 문제 해결 (CP949 → UTF-8, 21개 종목 수동 매핑)
- Supabase 페이지네이션 구현 (1,000개 제한 우회)
- **3단계 누적 필터링 로직** (가치평가 → 재무지표 → 섹터)
- TradingSettingsWithUniverse 컴포넌트 (1,100+ lines)
</details>

<details>
<summary><b>Task 14: 백테스트 필터링 시스템</b> [완료: 2025-09-07]</summary>

- 5가지 필터링 모드 (사전/사후/하이브리드/실시간/없음)
- 투자자 동향 필터 (외국인/기관 보유비율, 순매수)
- 필터 저장/불러오기 (SaveFilterDialog, LoadFilterDialog)
- 백테스트 통합 (사전 필터링 종목 자동 로드)
- 백테스트 결과 목록 (BacktestResultsList)
</details>

<details>
<summary><b>Task 15: 전략 관리 시스템 개선</b> [완료: 2025-09-12]</summary>

- StrategyLoader 컴포넌트 (656 lines)
- 전략 조건 조합 시각화 (지표명 한글화, 단계별 플로우)
- 공개/비공개 전략 기능 (is_public, RLS 정책)
- 검색 및 정렬 (이름/날짜, 오름차순/내림차순)
- 전략 불러오기 버그 수정
</details>

<details>
<summary><b>Task 16: 빌드 최적화 및 배포</b> [완료: 2025-09-12]</summary>

- **청크 분할 최적화** (1.36MB → 5개 청크)
  - React vendor: 375KB
  - MUI vendor: 405KB
  - Supabase vendor: 122KB
- vite.config.ts manualChunks 설정
- terser → esbuild (안정성 향상)
- Vercel 자동 배포 연동
- 문서 정리 (DOCUMENTATION_STRUCTURE.md, PROJECT_OVERVIEW.md)
</details>

<details>
<summary><b>Task 17: 백테스트 엔진 고도화</b> [완료: 2025-09-13]</summary>

- backtest_engine_advanced.py (450+ lines)
- **멀티 종목 동시 백테스트**
- 분할 매수/매도 전략
- indicators_complete.py (250+ lines, 10개 지표)
- strategy_analyzer.py (매매 신호 생성, AND/OR 평가)
- StrategyAnalyzer.tsx (1,100+ lines, 전략 로직 해석)
</details>

<details>
<summary><b>Task 18: 키움 REST API 통합</b> [완료: 2025-09-14]</summary>

- **키움증권 REST API 토큰 발급 성공**
  - OAuth 2.0 구현 (mockapi.kiwoom.com)
  - 파라미터 형식 문제 해결 (appsecret → secretkey)
- **NAS REST API Bridge Server 구축**
  - Synology NAS Docker (IP: 192.168.50.150:8080)
  - FastAPI 서버 (kiwoom_bridge/main.py, 401 lines)
- **전체 2,878개 종목 수집**
  - pykrx 라이브러리 (KOSPI 959 + KOSDAQ 1,803 + KONEX 116)
  - stock_metadata 테이블
- **하이브리드 시세 조회**
  - 키움 API 500 에러 우회
  - pykrx 데이터 백업
</details>

<details>
<summary><b>Task 19: 목표수익률 단계별 매도</b> [완료: 2025-01-14]</summary>

- **3단계 부분 매도** (50%, 30%, 20%)
- **동적 손절 조정** (Break Even Stop)
  - 1단계 도달 → 손절을 본전으로
  - 2단계 도달 → 손절을 1단계 매도가로
- **단계별 AND/OR 결합**
- TargetProfitSettingsEnhanced 컴포넌트
- test_staged_profit.py 테스트
</details>

---

### 🔥 **Task 20: Phase 2.5a - 표준화 및 안정성 강화** [✅ 완료: 2025-10-01]

#### 배경 및 문제 상황
**백테스트 "거래 0회" 오류 발생**:
- MACD 지표 컬럼명 불일치 (`macd` vs `macd_signal` vs `MACD`)
- 프론트엔드: `indicator/compareTo` 형식
- 백엔드: `left/right` 형식 기대
- Supabase 템플릿: 구 형식 사용
- 데이터 재현성 부재 (동일 기간 백테스트 시 다른 결과)

#### 구현 내용

##### 1. 지표-컬럼 매핑 표준 테이블 (`sql/02_indicator_columns_standard.sql`)
```sql
CREATE TABLE IF NOT EXISTS indicator_columns (
    indicator_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    column_type TEXT DEFAULT 'numeric',
    is_primary BOOLEAN DEFAULT false,
    UNIQUE(indicator_name, column_name)
);

-- 10개 핵심 지표 등록
INSERT INTO indicator_columns VALUES
    ('macd', 'macd', 'numeric', true),
    ('macd', 'macd_signal', 'numeric', false),
    ('macd', 'macd_hist', 'numeric', false),
    ('rsi', 'rsi', 'numeric', true),
    ('sma', 'sma_{period}', 'numeric', true),
    -- ... 나머지 지표
```

**효과**: 지표명-컬럼명 계약 정의로 불일치 방지

##### 2. 샌드박스 실행 환경 강화 (`backend/indicators/sandbox.py`)
```python
class SafeExecutor:
    def execute(self, code, df, params, expected_columns):
        # AST 기반 코드 검증
        is_valid, error_msg = EnhancedSecuritySandbox.validate_ast(code)

        # Timeout (5초)
        signal.alarm(int(self.limits.timeout_seconds))

        # Memory Limit (512MB)
        resource.setrlimit(resource.RLIMIT_AS,
            (self.limits.memory_bytes, self.limits.memory_bytes))

        # 실행
        exec(code, namespace)

        # 출력 스키마 검증
        validate_output_schema(result, expected_columns)
```

**효과**: DB 저장 코드 안전 실행, 타임아웃/메모리 제한

##### 3. 프리플라이트 검증 시스템 (`backend/backtest/preflight.py`)
```python
@staticmethod
def extract_columns(condition: Dict[str, Any]) -> Set[str]:
    """양쪽 형식 지원"""
    columns = set()

    # Format 1: left/right
    for side in ['left', 'right']:
        operand = condition.get(side)
        if operand and isinstance(operand, str):
            if not ConditionParser._is_numeric(operand):
                columns.add(operand)

    # Format 2: indicator/compareTo
    indicator = condition.get('indicator')
    if indicator:
        columns.add(indicator)

    compare_to = condition.get('compareTo')
    if compare_to:
        columns.add(compare_to)

    return columns
```

**효과**:
- 백테스트 실행 전 지표 존재 여부 검증
- 구 형식 + 신 형식 모두 지원 (마이그레이션 기간)
- 순환 참조 감지

##### 4. 프론트엔드 자동 변환 (`src/utils/conditionConverter.ts`)
```typescript
export const convertConditionToStandard = (
  oldCondition: OldCondition
): StandardCondition => {
  const left = normalizeIndicatorName(oldCondition.indicator)
  const operator = OPERATOR_MAPPING[oldCondition.operator] || oldCondition.operator
  const right = typeof oldCondition.value === 'string'
    ? normalizeIndicatorName(oldCondition.value)
    : oldCondition.value

  return { left, operator, right }
}

const OPERATOR_MAPPING = {
  'cross_above': 'crossover',
  'cross_below': 'crossunder',
  '=': '==',
}
```

**효과**:
- StrategyBuilder 저장 시 자동 변환
- 사용자 개입 없이 표준 형식 적용

##### 5. StrategyBuilder 통합 (`src/components/StrategyBuilder.tsx`)
```typescript
// Line 81: Import
import { ensureStandardFormat } from '../utils/conditionConverter'

// Line 601-606: 저장 시 변환
const convertedStrategy = ensureStandardFormat({
  buyConditions: strategy.buyConditions,
  sellConditions: strategy.sellConditions
})
console.log('[StrategyBuilder] Converted to standard format:', convertedStrategy)

// Line 625: 지표 형식 표준화
const indicatorConfig: any = {
  name: ind.id.toLowerCase().replace('_', ''),  // sma_20 → sma
  type: ind.id.toUpperCase(),  // SMA
  params: ind.params || {}
}
```

#### 테스트 및 배포 상태
- ✅ 프론트엔드 빌드 성공 (1,484KB → 456KB gzipped)
- ✅ TypeScript 컴파일 통과
- ✅ BacktestRunner.tsx 타입 에러 수정
- ⏳ NAS 서버 배포 대기
- ⏳ Supabase 템플릿 재생성 대기

#### 산출물
| 파일명 | 설명 | 상태 |
|--------|------|------|
| `sql/02_indicator_columns_standard.sql` | 지표-컬럼 매핑 테이블 | ✅ |
| `backend/indicators/sandbox.py` | 샌드박스 실행 환경 | ✅ |
| `backend/backtest/preflight.py` | 프리플라이트 검증 | ✅ |
| `src/utils/conditionConverter.ts` | 자동 변환 유틸 | ✅ |
| `src/components/StrategyBuilder.tsx` | 통합 적용 | ✅ |
| `sql/04_reset_strategies_with_standard_templates.sql` | 템플릿 재생성 | 준비 완료 |
| `docs/testing/FRONTEND_AUTO_CONVERSION_TEST.md` | 테스트 가이드 | ✅ |

---

### ✅ **Task 20 (완료): n8n 워크플로우 모니터링 시스템**

**기간**: 2025-09 - 2025-10-20
**진행률**: 100%

#### 완료된 작업
- ✅ n8n 서버 설정 (NAS Docker 컨테이너, 최신 버전)
- ✅ nginx 리버스 프록시 구축 (CORS 문제 해결)
- ✅ Docker 네트워크 설정 (nginx ↔ n8n 통신)
- ✅ n8n API 클라이언트 라이브러리 개발 (`src/lib/n8n.ts`)
  - TypeScript 인터페이스 정의
  - 워크플로우 조회 API
  - 실행 내역 조회 API
  - 노드별 실행 상태 분석
- ✅ n8n 워크플로우 모니터링 UI (`src/components/N8nWorkflowMonitor.tsx`)
  - 실시간 워크플로우 활동 대시보드
  - 4개 통계 카드 (성공/실패/성공률/총 실행횟수)
  - 워크플로우별 상세 정보 (아코디언 형식)
  - 노드별 실행 상태 테이블
  - 30초 자동 새로고침
- ✅ 자동매매 탭 통합
- ✅ CORS 이슈 해결
  - nginx에서 CORS 헤더 처리
  - preflight OPTIONS 요청 지원
  - API Key 헤더 전달

#### 기술 스택
- **백엔드**: n8n latest (Docker), nginx (리버스 프록시)
- **프론트엔드**: React 18, TypeScript, Material-UI
- **통신**: REST API, CORS 설정
- **포트**: nginx:5679 → n8n:5678

#### 다음 단계
- 실시간 전략 모니터링 (활성 전략 체크, 매매 신호 생성)
- 자동 주문 실행 (매수/매도 자동화, 체결 확인)
- 키움 API 연동 노드 개발

---

### 📋 **Task 21-26: 대기 중인 작업**

<details>
<summary><b>Task 21: 성과 분석 대시보드</b> [대기: 0%]</summary>

**예상 기간**: 2025-10 (2주)

- 수익률 분석 (일/주/월/년, CAGR, 위험 조정 수익률)
- 포트폴리오 분석 (자산 배분, 섹터 배분, 상관관계)
- 벤치마크 비교 (KOSPI/KOSDAQ 대비, 알파/베타)
- 리스크 모니터링 (VaR, CVaR, 스트레스 테스트)
- 리포트 생성 (일일/월간 PDF, Excel 추출)
</details>

<details>
<summary><b>Task 22: AI 포트폴리오 최적화</b> [대기: 0%]</summary>

**예상 기간**: 2025-10 (3주)

- ML 모델 개발 (LSTM 가격 예측, Random Forest 종목 선택)
- 포트폴리오 최적화 (Mean-Variance, Black-Litterman, Risk Parity)
- 리밸런싱 자동화 (주기적, 임계값 기반, 세금 최적화)
- AI 추천 시스템 (종목/타이밍/포트폴리오 구성 추천)
- 백테스팅 검증 (Walk-forward, Out-of-sample)
</details>

<details>
<summary><b>Task 23: 알림 시스템</b> [대기: 0%]</summary>

**예상 기간**: 2025-10 (1주)

- 이메일 알림 (SendGrid, 일일 요약, 거래 확인)
- 텔레그램 봇 (실시간 알림, 명령어 조회, 차트 전송)
- 푸시 알림 (FCM, iOS/Android, Web Push)
- 알림 설정 (유형별 ON/OFF, 시간대, 빈도 제한)
- 알림 관리 (히스토리, 읽음/안읽음, 검색)
</details>

<details>
<summary><b>Task 24: 모바일 반응형 UI</b> [대기: 0%]</summary>

**예상 기간**: 2025-11 (2주)

- 반응형 레이아웃 (모바일 브레이크포인트, 터치 UI, 스와이프)
- 모바일 최적화 (레이지 로딩, 코드 스플리팅, 캐싱)
- PWA 구현 (Service Worker, Manifest, 홈 화면 추가)
- 모바일 전용 기능 (생체 인증, 퀵 액션, 위젯)
- 성능 최적화 (Virtual scrolling, Debounce/Throttle)
</details>

<details>
<summary><b>Task 25: 테스트 및 최적화</b> [대기: 0%]</summary>

**예상 기간**: 2025-11 (2주)

- 단위 테스트 (Jest, React Testing Library, 커버리지 80%)
- 통합 테스트 (Cypress E2E, 크로스 브라우저)
- 성능 최적화 (Lighthouse, Bundle 크기, Tree shaking)
- 보안 점검 (OWASP Top 10, SQL Injection, XSS, CSRF)
- 접근성 개선 (WCAG 2.1, 키보드 네비게이션, ARIA labels)
</details>

<details>
<summary><b>Task 26: 문서화 및 배포</b> [대기: 0%]</summary>

**예상 기간**: 2025-12 (1주)

- API 문서화 (OpenAPI 3.0, Swagger UI, 예제 코드)
- 사용자 가이드 (온보딩, 기능별 설명, 비디오, FAQ)
- 개발자 문서 (아키텍처, Storybook, 코드 컨벤션)
- Vercel 배포 (환경 변수, Custom domain, Preview deployments)
- 모니터링 설정 (Sentry, Google Analytics, Performance, Uptime)
</details>

---

## 🎯 즉시 해야 할 작업 (우선순위 순)

### 1. ⚡ **NAS 서버 배포** [30분]

**목적**: Phase 2.5a 최신 백엔드 배포

```bash
# 1. 스크립트 실행
cd D:\Dev\auto_stock\scripts\deployment
bash deploy_backend_to_nas.sh

# 2. 배포 확인
curl http://192.168.50.150:8001/health

# 3. 백테스트 테스트
python test_nas_backtest.py
```

**배포 파일**:
- `backend/backtest/preflight.py` (양쪽 형식 지원)
- `backend/indicators/calculator.py` (DB 전용 모드)
- `backend/indicators/sandbox.py` (보안 강화)

---

### 2. 🗄️ **Supabase 템플릿 전략 재생성** [10분]

**현재 문제**: 템플릿 전략이 구 형식(`indicator/compareTo`) 사용 중

**해결책**: 표준 형식으로 재생성

```bash
# Supabase SQL Editor에서 실행
# sql/04_reset_strategies_with_standard_templates.sql 내용 복사/실행
```

**포함된 템플릿** (10개):
1. MACD 시그널
2. RSI 과매도 반등
3. 골든크로스
4. 볼린저밴드 돌파
5. 스토캐스틱 과매도
6. 이동평균 3선 정렬
7. ADX 추세 강도
8. OBV 거래량 확인
9. ATR 변동성 돌파
10. VWAP 가격 괴리

---

### 3. 🧪 **엔드투엔드 테스트** [1시간]

**시나리오 A: 새 전략 생성 → 백테스트**
1. StrategyBuilder에서 새 전략 생성
2. 지표: SMA(20), SMA(50)
3. 매수: `sma_20 crossover sma_50`
4. 저장 → 콘솔 로그 확인 (표준 형식 변환)
5. 백테스트 실행 → 거래 발생 확인

**시나리오 B: 템플릿 전략 사용**
1. "MACD 시그널" 템플릿 로드
2. 백테스트 실행
3. 거래 내역 확인 (0회 아님을 확인)

**시나리오 C: 기존 전략 편집**
1. Supabase의 구 형식 전략 로드
2. StrategyBuilder에서 편집
3. 저장 → 자동 변환 확인
4. 백테스트 실행

**테스트 문서**: [docs/testing/FRONTEND_AUTO_CONVERSION_TEST.md](docs/testing/FRONTEND_AUTO_CONVERSION_TEST.md)

---

### 4. 📊 **Phase 2.5b 착수** [2-3일]

**목표**: 백테스트 결과를 100% 재현 가능하게 만들기

#### Step 1: `sql/05_dataset_versioning.sql` 작성
```sql
CREATE TABLE price_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    data_hash TEXT NOT NULL,  -- SHA256(정렬된 OHLCV 데이터)
    row_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_code, start_date, end_date, data_hash)
);

ALTER TABLE backtest_results
ADD COLUMN dataset_id UUID REFERENCES price_datasets(id);
```

#### Step 2: `backend/backtest/dataset_manager.py` 구현
```python
def generate_dataset_hash(df: pd.DataFrame) -> str:
    """정렬된 OHLCV 데이터의 SHA256 해시 생성"""
    sorted_df = df.sort_index()
    data_bytes = sorted_df.to_json().encode('utf-8')
    return hashlib.sha256(data_bytes).hexdigest()

async def get_or_create_dataset(stock_code, start_date, end_date, price_df):
    data_hash = generate_dataset_hash(price_df)

    # 기존 데이터셋 조회
    existing = await supabase.from_('price_datasets') \
        .select('id') \
        .eq('stock_code', stock_code) \
        .eq('data_hash', data_hash) \
        .single()

    if existing:
        return existing['id']

    # 새 데이터셋 생성
    result = await supabase.from_('price_datasets').insert({
        'stock_code': stock_code,
        'start_date': start_date,
        'end_date': end_date,
        'data_hash': data_hash,
        'row_count': len(price_df)
    }).single()

    return result['id']
```

#### Step 3: `backend/backtest/runner.py` 수정
```python
# 백테스트 실행 시 dataset_id 기록
dataset_id = await dataset_manager.get_or_create_dataset(
    stock_code, start_date, end_date, price_df
)

result = {
    "dataset_id": dataset_id,
    "trades": trades,
    "performance": metrics
}
```

#### Step 4: 프론트엔드에 "데이터 버전" 표시 추가
```typescript
// BacktestResults.tsx에 dataset_id 표시
<Chip label={`데이터 버전: ${result.dataset_id.slice(0, 8)}`} />
```

**검증 방법**:
```sql
-- 동일 전략 + 동일 기간 → 동일 dataset_id 확인
SELECT
  br.id,
  br.dataset_id,
  pd.data_hash,
  br.total_trades
FROM backtest_results br
JOIN price_datasets pd ON br.dataset_id = pd.id
WHERE br.strategy_id = '특정_전략_UUID'
ORDER BY br.created_at DESC
LIMIT 10;
```

---

## 🔮 향후 계획 (Phase 3-4)

### Phase 3: API/워커 분리 [2-3주]

**문제점**: 현재 단일 프로세스에서 API + 백테스트 실행 → 느린 백테스트 시 API 응답 지연

**해결책**: Redis 기반 작업 큐 시스템

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FastAPI   │─────▶│    Redis    │◀─────│   Worker    │
│  (API만)    │      │  (작업 큐)   │      │(백테스트)    │
└─────────────┘      └─────────────┘      └─────────────┘
      │                                           │
      └───────────────────┬───────────────────────┘
                          ▼
                  ┌─────────────┐
                  │  Supabase   │
                  │  (결과 저장) │
                  └─────────────┘
```

**구현 계획**:
1. Redis 작업 큐 (`backend/queue/redis_queue.py`)
2. 워커 프로세스 (`backend/workers/backtest_worker.py`)
3. API 엔드포인트 수정 (비동기 작업 생성 → 작업 ID 반환)
4. 프론트엔드 폴링 (작업 ID로 진행률 조회)

---

### Phase 4: Windows Execution Agent [3-4주]

**문제점**: 키움 API는 Windows 32bit에서만 동작 → Linux NAS에서 실행 불가

**해결책**: Windows PC에서 키움 API 전용 에이전트 실행

```
┌─────────────┐      gRPC       ┌──────────────────┐
│   NAS API   │◀───────────────▶│  Windows Agent   │
│  (Linux)    │                 │  (32bit Python)  │
└─────────────┘                 └──────────────────┘
                                         │
                                         ▼
                                 ┌──────────────┐
                                 │  키움 OpenAPI │
                                 └──────────────┘
```

**구현 계획**:
1. gRPC 프로토콜 정의 (`proto/kiwoom_agent.proto`)
2. Windows 에이전트 (`windows_agent/kiwoom_service.py`)
3. NAS 클라이언트 (`backend/kiwoom/grpc_client.py`)
4. 상태 모니터링 (하트비트, 자동 재연결)

---

## 📂 프로젝트 폴더 구조

```
auto_stock/
├── docs/
│   ├── architecture/          # 아키텍처 설계
│   │   ├── ARCHITECTURE_UPGRADE_PLAN.md
│   │   └── STANDARD_STRATEGY_FORMAT.md
│   ├── deployment/            # 배포 관련
│   │   ├── NAS_DEPLOYMENT_FILES.md
│   │   ├── NAS_FOLDER_STRUCTURE.md
│   │   └── PHASE_2.5_DEPLOYMENT.md
│   ├── testing/               # 테스트 가이드
│   │   └── FRONTEND_AUTO_CONVERSION_TEST.md
│   ├── guides/                # 사용자 가이드
│   │   ├── fix-strategy-loading.md
│   │   └── fix-vercel-deployment.md
│   └── development/           # 개발 문서
│       └── DEVELOPMENT_ROADMAP.md
│
├── backend/
│   ├── backtest/
│   │   ├── preflight.py       # ✅ 최신 (양쪽 형식 지원)
│   │   ├── runner.py
│   │   └── dataset_manager.py # 🔜 구현 예정
│   ├── indicators/
│   │   ├── calculator.py      # ✅ DB 전용 모드
│   │   └── sandbox.py         # ✅ 보안 강화
│   └── api/
│       └── backtest.py
│
├── src/
│   ├── components/
│   │   ├── StrategyBuilder.tsx  # ✅ 자동 변환 적용
│   │   └── BacktestRunner.tsx   # ✅ 타입 에러 수정
│   └── utils/
│       └── conditionConverter.ts # ✅ 신규
│
├── sql/
│   ├── 02_indicator_columns_standard.sql  # ✅ 완료
│   ├── 04_reset_strategies_with_standard_templates.sql  # 🔜 실행 필요
│   ├── 05_dataset_versioning.sql          # 🔜 구현 예정
│   └── scripts/
│       └── check_strategy_config.sql
│
├── scripts/
│   └── deployment/
│       ├── deploy_backend_to_nas.sh
│       ├── deploy_to_nas.bat
│       ├── check_nas_logs.bat
│       ├── test_nas_api.py
│       └── test_nas_backtest.py
│
├── config/
│   └── docker/
│       ├── docker-compose.auto-stock.yml
│       ├── docker-compose.hybrid.yml
│       └── docker-compose.nas.yml
│
├── .taskmaster/
│   ├── tasks/tasks.json       # TaskMaster 작업 관리
│   └── config.json
│
├── MASTER_ROADMAP.md          # ✅ 이 파일 (마스터 계획)
└── README.md                  # 프로젝트 소개
```

---

## 🎓 핵심 개념 정리

### 1. 전략 조건 형식 표준화

#### 구 형식 (레거시)
```json
{
  "buyConditions": [
    {"indicator": "MACD", "operator": "cross_above", "compareTo": "MACD_SIGNAL"}
  ]
}
```

#### 표준 형식 (현재)
```json
{
  "buyConditions": [
    {"left": "macd", "operator": "crossover", "right": "macd_signal"}
  ]
}
```

#### 자동 변환 매핑
| 구 형식 | 표준 형식 |
|---------|-----------|
| `cross_above` | `crossover` |
| `cross_below` | `crossunder` |
| `indicator` | `left` |
| `compareTo` | `right` |
| `value` | `right` (숫자인 경우) |

---

### 2. 지표-컬럼 매핑

| 지표명 | 컬럼명 | 설명 |
|--------|--------|------|
| `macd` | `macd`, `macd_signal`, `macd_hist` | MACD 지표 3개 컬럼 |
| `rsi` | `rsi` | RSI 단일 컬럼 |
| `sma` | `sma_{period}` | 예: `sma_20`, `sma_50` |
| `ema` | `ema_{period}` | 예: `ema_12`, `ema_26` |
| `bb` | `bb_upper`, `bb_middle`, `bb_lower` | 볼린저밴드 3개 밴드 |
| `stoch` | `stoch_k`, `stoch_d` | 스토캐스틱 2개 라인 |
| `adx` | `adx`, `plus_di`, `minus_di` | ADX 3개 컬럼 |

**표준 테이블**: `indicator_columns` ([sql/02_indicator_columns_standard.sql](sql/02_indicator_columns_standard.sql))

---

### 3. 백테스트 데이터 재현성 (Phase 2.5b)

#### 문제 상황
- 동일 전략 + 동일 기간 → 다른 결과 발생 가능
- 원인: Supabase 데이터가 업데이트되면 과거 백테스트 재현 불가

#### 해결책: dataset_id
```
백테스트 실행
    ↓
주가 데이터 조회 (Supabase)
    ↓
데이터 해시 생성 (SHA256)
    ↓
price_datasets 테이블에서 조회/생성
    ↓
dataset_id를 backtest_results에 기록
```

**장점**:
- 과거 백테스트 결과 100% 재현 가능
- 데이터 변경 감지 (해시 불일치 시 경고)
- 동일 데이터 재사용 (중복 저장 방지)

---

## 🐛 알려진 이슈 및 해결 상태

| 이슈 | 상태 | 해결 방법 |
|------|------|-----------|
| 백테스트 "거래 0회" 오류 | ✅ 해결 | preflight.py 양쪽 형식 지원 |
| MACD 컬럼명 불일치 | ✅ 해결 | indicator_columns 표준 테이블 |
| 프론트엔드 형식 불일치 | ✅ 해결 | conditionConverter.ts 자동 변환 |
| 템플릿 전략 구 형식 사용 | 🔜 해결 예정 | SQL 04번 실행 필요 |
| 백테스트 결과 재현 불가 | 🔜 해결 예정 | Phase 2.5b (dataset_id) |
| 백테스트 중 API 타임아웃 | 📋 계획됨 | Phase 3 (Redis 워커) |
| 키움 API Linux 미지원 | 📋 계획됨 | Phase 4 (Windows Agent) |

---

## 📞 문제 발생 시 체크리스트

### 백테스트 오류 발생 시

1. **NAS 서버 로그 확인**
   ```bash
   cd scripts/deployment
   bash check_nas_logs.bat
   # 또는
   docker logs backend_container | grep "Preflight"
   ```

2. **전략 형식 확인**
   ```sql
   SELECT config FROM strategies WHERE id = '오류_발생한_전략_UUID';
   ```
   - `left/right` 형식인지 확인
   - `indicator/compareTo` 형식이면 StrategyBuilder에서 재저장

3. **지표 데이터 확인**
   ```sql
   SELECT column_name
   FROM information_schema.columns
   WHERE table_name = 'indicators'
   AND column_name LIKE '%macd%';
   ```

4. **Preflight 검증 실행**
   ```python
   # scripts/deployment/test_nas_api.py 수정하여 실행
   response = requests.post("http://192.168.50.150:8001/api/backtest/validate",
       json={"strategy_id": "UUID"})
   print(response.json())
   ```

---

## 🎯 다음 체크포인트

### 1주일 내 목표
- [ ] NAS 서버 최신 백엔드 배포 완료
- [ ] Supabase 템플릿 전략 재생성
- [ ] 엔드투엔드 테스트 통과 (3개 시나리오)
- [ ] Phase 2.5b SQL 스키마 작성 완료

### 1개월 내 목표
- [ ] dataset_id 시스템 구현 완료
- [ ] JSON Schema 검증 시스템 구현
- [ ] Redis 작업 큐 시스템 설계 시작

### 3개월 내 목표
- [ ] API/워커 분리 완료
- [ ] Windows Execution Agent 프로토타입
- [ ] 실전 투자 모니터링 대시보드

---

## 📚 참고 문서

### 아키텍처
- [ARCHITECTURE_UPGRADE_PLAN.md](docs/architecture/ARCHITECTURE_UPGRADE_PLAN.md)
- [STANDARD_STRATEGY_FORMAT.md](docs/architecture/STANDARD_STRATEGY_FORMAT.md)

### 배포
- [NAS_DEPLOYMENT_FILES.md](docs/deployment/NAS_DEPLOYMENT_FILES.md)
- [NAS_FOLDER_STRUCTURE.md](docs/deployment/NAS_FOLDER_STRUCTURE.md)
- [PHASE_2.5_DEPLOYMENT.md](docs/deployment/PHASE_2.5_DEPLOYMENT.md)

### 테스트
- [FRONTEND_AUTO_CONVERSION_TEST.md](docs/testing/FRONTEND_AUTO_CONVERSION_TEST.md)

### 가이드
- [fix-strategy-loading.md](docs/guides/fix-strategy-loading.md)
- [fix-vercel-deployment.md](docs/guides/fix-vercel-deployment.md)

### 개발
- [DEVELOPMENT_ROADMAP.md](docs/development/DEVELOPMENT_ROADMAP.md)

---

## 📊 프로젝트 통계

- **총 코드 라인**: ~35,000 lines
- **프론트엔드**: 18,000 lines (TypeScript/React)
- **백엔드**: 12,000 lines (Python)
- **SQL**: 3,000 lines
- **문서**: 2,000 lines (Markdown)

- **총 컴포넌트**: 85개
- **총 API 엔드포인트**: 42개
- **총 데이터베이스 테이블**: 28개

---

**작성자**: Claude Code
**최종 수정**: 2025-10-01
**버전**: 2.0
