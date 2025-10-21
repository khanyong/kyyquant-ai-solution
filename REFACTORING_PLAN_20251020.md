# 리팩토링 계획서 (Refactoring Plan)

> **작성일**: 2025-10-20
> **목적**: 대형 컴포넌트 분할 및 코드 품질 개선
> **원칙**: 외부 동작 유지, 점진적 개선, 테스트 기반

---

## 📊 현황 분석

### 문제가 있는 파일 (100KB 이상)

| 파일 | 크기 | 줄 수 | 우선순위 |
|------|------|-------|----------|
| `src/components/TradingSettingsWithUniverse.tsx` | 104KB | 2,374줄 | 🔴 긴급 |
| `src/pages/InvestmentSettingsComplete.tsx` | 100KB | 2,451줄 | 🔴 긴급 |
| `src/components/StrategyAnalyzer.tsx` | 92KB | 1,755줄 | 🟡 높음 |
| `src/components/StrategyBuilder.tsx` | 88KB | 2,272줄 | 🟡 높음 |
| `src/components/BacktestRunner.tsx` | 80KB | 1,829줄 | 🟢 중간 |

### 삭제 대상 백업 파일

- `src/pages/MyPage-backup.tsx` (25KB)
- `src/components/StrategyAnalysis_old.tsx` (28KB)

---

## 🎯 리팩토링 목표

### 단기 목표 (2주)
- ✅ 100KB 이상 파일 2개 분할
- ✅ 백업 파일 제거
- ✅ 공통 컴포넌트 추출

### 중기 목표 (1개월)
- 모든 80KB 이상 파일 분할
- Custom Hooks 체계화
- 유틸리티 함수 모듈화

### 장기 목표 (3개월)
- Feature-based 아키텍처 전환
- 컴포넌트 크기 제한 규칙 (500줄)
- Code Splitting 적용

---

## 📋 Phase 1: 백업 파일 정리 (즉시)

### 작업 내용
```bash
# 불필요한 백업 파일 삭제
rm src/pages/MyPage-backup.tsx
rm src/components/StrategyAnalysis_old.tsx

# Git 커밋
git add .
git commit -m "chore: 백업 파일 정리"
```

### 예상 효과
- 53KB 용량 절감
- 코드베이스 정리

---

## 📋 Phase 2: TradingSettingsWithUniverse.tsx 분할 (1주차)

### 현재 구조 (2,374줄)
```
TradingSettingsWithUniverse.tsx
├─ 종목 선택 UI (UniverseSelector) - 500줄
├─ 지표 설정 UI (IndicatorSettings) - 600줄
├─ 매매 설정 폼 (TradingForm) - 400줄
├─ 차트 표시 (ChartPanel) - 300줄
├─ 비즈니스 로직 - 300줄
└─ 유틸리티 함수 - 274줄
```

### 목표 구조
```
features/trading/
├─ components/
│  ├─ TradingSettingsWithUniverse.tsx (200줄) - 메인 컨테이너
│  ├─ UniverseSelector.tsx (400줄)
│  ├─ IndicatorSettings.tsx (500줄)
│  ├─ TradingForm.tsx (350줄)
│  └─ ChartPanel.tsx (250줄)
├─ hooks/
│  ├─ useTradingSettings.ts (200줄)
│  ├─ useUniverseData.ts (150줄)
│  └─ useIndicatorConfig.ts (120줄)
└─ utils/
   ├─ tradingValidation.ts (100줄)
   └─ tradingCalculations.ts (104줄)
```

### 단계별 작업

#### Step 1: 유틸리티 함수 추출
```typescript
// Before: TradingSettingsWithUniverse.tsx 내부
const calculateStopLoss = (price, percent) => { ... }
const validateIndicator = (config) => { ... }

// After: utils/tradingCalculations.ts
export const calculateStopLoss = (price: number, percent: number): number => { ... }

// After: utils/tradingValidation.ts
export const validateIndicator = (config: IndicatorConfig): boolean => { ... }
```

**커밋**: `refactor(trading): 유틸리티 함수 추출`

#### Step 2: Custom Hooks 추출
```typescript
// Before: TradingSettingsWithUniverse.tsx
const [settings, setSettings] = useState()
const [loading, setLoading] = useState()
useEffect(() => { ... }, [])

// After: hooks/useTradingSettings.ts
export const useTradingSettings = () => {
  const [settings, setSettings] = useState()
  const [loading, setLoading] = useState()

  useEffect(() => { ... }, [])

  return { settings, loading, updateSettings }
}
```

**커밋**: `refactor(trading): Custom Hooks 추출`

#### Step 3: 컴포넌트 분할
```typescript
// components/UniverseSelector.tsx
export const UniverseSelector: React.FC<UniverseSelectorProps> = ({ ... }) => {
  return (
    <Box>
      {/* 종목 선택 UI */}
    </Box>
  )
}

// components/IndicatorSettings.tsx
export const IndicatorSettings: React.FC<IndicatorSettingsProps> = ({ ... }) => {
  return (
    <Box>
      {/* 지표 설정 UI */}
    </Box>
  )
}
```

**커밋**: `refactor(trading): 컴포넌트 분할 - UniverseSelector, IndicatorSettings`

#### Step 4: 메인 컨테이너 정리
```typescript
// TradingSettingsWithUniverse.tsx (최종)
export default function TradingSettingsWithUniverse() {
  const { settings, loading, updateSettings } = useTradingSettings()
  const { universeData } = useUniverseData()

  return (
    <Container>
      <UniverseSelector data={universeData} />
      <IndicatorSettings settings={settings} onChange={updateSettings} />
      <TradingForm settings={settings} onSubmit={handleSubmit} />
      <ChartPanel data={chartData} />
    </Container>
  )
}
```

**커밋**: `refactor(trading): 메인 컨테이너 정리`

### 테스트 체크리스트
- [ ] 종목 선택 기능 정상 작동
- [ ] 지표 설정 저장/로드
- [ ] 매매 설정 폼 제출
- [ ] 차트 표시 확인
- [ ] 빌드 에러 없음
- [ ] 기존 기능 모두 동작

---

## 📋 Phase 3: InvestmentSettingsComplete.tsx 분할 (2주차)

### 현재 구조 (2,451줄)
```
InvestmentSettingsComplete.tsx
├─ 투자 설정 폼 - 700줄
├─ 포트폴리오 배분 - 600줄
├─ 리스크 관리 - 500줄
├─ 목표 수익률 설정 - 400줄
└─ 비즈니스 로직 - 251줄
```

### 목표 구조
```
features/investment/
├─ components/
│  ├─ InvestmentSettingsComplete.tsx (200줄)
│  ├─ InvestmentForm.tsx (500줄)
│  ├─ PortfolioAllocation.tsx (450줄)
│  ├─ RiskManagement.tsx (400줄)
│  └─ TargetProfitSettings.tsx (350줄)
├─ hooks/
│  ├─ useInvestmentSettings.ts (200줄)
│  ├─ usePortfolioCalculation.ts (150줄)
│  └─ useRiskAnalysis.ts (120줄)
└─ utils/
   ├─ portfolioCalculations.ts (150줄)
   └─ riskMetrics.ts (100줄)
```

### 작업 단계
1. 포트폴리오 계산 로직 추출
2. 리스크 분석 함수 모듈화
3. 각 섹션별 컴포넌트 분리
4. Custom Hooks로 상태 관리 통합

---

## 📋 Phase 4: StrategyBuilder.tsx 분할 (3주차)

### 목표 구조
```
features/strategy/
├─ components/
│  ├─ StrategyBuilder.tsx (300줄)
│  ├─ ConditionBuilder.tsx (400줄)
│  ├─ IndicatorSelector.tsx (350줄)
│  ├─ BacktestPreview.tsx (300줄)
│  └─ StrategyValidation.tsx (200줄)
├─ hooks/
│  ├─ useStrategyBuilder.ts (200줄)
│  └─ useBacktestSimulation.ts (180줄)
└─ utils/
   ├─ strategyValidation.ts (150줄)
   └─ conditionParser.ts (120줄)
```

---

## 📋 Phase 5: 공통 컴포넌트 추출 (4주차)

### 목표
```
src/components/common/
├─ forms/
│  ├─ FormSection.tsx
│  ├─ FormField.tsx
│  ├─ NumberInput.tsx
│  └─ SelectInput.tsx
├─ charts/
│  ├─ BaseChart.tsx
│  ├─ CandlestickChart.tsx
│  └─ LineChart.tsx
├─ tables/
│  ├─ DataTable.tsx
│  └─ SortableTable.tsx
└─ feedback/
   ├─ LoadingSpinner.tsx
   └─ ErrorMessage.tsx
```

### 재사용 가능한 패턴 추출
- 반복되는 폼 패턴
- 차트 래퍼 컴포넌트
- 테이블 구성 요소
- 로딩/에러 처리

---

## 📋 Phase 6: Feature-based 아키텍처 전환 (5-8주차)

### 현재 구조
```
src/
├─ components/ (모든 컴포넌트)
├─ pages/ (모든 페이지)
├─ hooks/ (모든 훅)
└─ utils/ (모든 유틸)
```

### 목표 구조
```
src/
├─ features/
│  ├─ trading/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ utils/
│  │  ├─ services/
│  │  └─ types/
│  ├─ backtest/
│  ├─ strategy/
│  ├─ investment/
│  └─ portfolio/
├─ shared/
│  ├─ components/
│  ├─ hooks/
│  └─ utils/
└─ core/
   ├─ services/
   └─ types/
```

### 마이그레이션 전략
1. 새 디렉토리 구조 생성
2. 한 번에 하나의 feature 이동
3. Import 경로 업데이트
4. 테스트 실행 및 검증

---

## 📋 Phase 7: Code Splitting 적용 (병행 작업)

### 목표
- 초기 번들 크기 50% 감소
- 페이지별 lazy loading
- 큰 라이브러리 dynamic import

### 구현
```typescript
// AppWithRouter.tsx
const TradingSettingsWithUniverse = lazy(() =>
  import('./features/trading/components/TradingSettingsWithUniverse')
)
const InvestmentSettingsComplete = lazy(() =>
  import('./features/investment/components/InvestmentSettingsComplete')
)
const StrategyBuilder = lazy(() =>
  import('./features/strategy/components/StrategyBuilder')
)

// Suspense 래퍼
<Suspense fallback={<LoadingSpinner />}>
  <TradingSettingsWithUniverse />
</Suspense>
```

### Chart 라이브러리 최적화
```typescript
// Before
import { Chart } from 'chart.js'

// After
const Chart = lazy(() => import('chart.js'))
```

---

## 🛡️ 리팩토링 안전 수칙

### 1. 항상 테스트 먼저
```bash
# 리팩토링 전
npm run build
npm run test (if available)
# 수동 테스트: 주요 기능 확인
```

### 2. 작은 단위로 커밋
```bash
# ❌ 나쁜 예
git commit -m "리팩토링"

# ✅ 좋은 예
git commit -m "refactor(trading): UniverseSelector 컴포넌트 추출"
git commit -m "refactor(trading): useTradingSettings 훅 추출"
```

### 3. 기능 테스트 후 다음 단계
- 리팩토링 → 테스트 → 커밋 → 다음 작업
- 문제 발생 시 즉시 롤백 가능

### 4. PR 단위 분리
```
PR #1: 백업 파일 정리
PR #2: TradingSettings 유틸 추출
PR #3: TradingSettings 훅 추출
PR #4: TradingSettings 컴포넌트 분할
```

---

## 📊 진행 상황 추적

### Week 1
- [ ] 백업 파일 삭제
- [ ] TradingSettings 유틸 추출
- [ ] TradingSettings 훅 추출
- [ ] TradingSettings 컴포넌트 분할 (50%)

### Week 2
- [ ] TradingSettings 컴포넌트 분할 완료
- [ ] InvestmentSettings 유틸 추출
- [ ] InvestmentSettings 훅 추출

### Week 3
- [ ] InvestmentSettings 컴포넌트 분할
- [ ] StrategyBuilder 분할 시작

### Week 4
- [ ] StrategyBuilder 분할 완료
- [ ] 공통 컴포넌트 추출

---

## 📈 성공 지표

### 정량적 지표
- [ ] 500줄 이상 파일 개수: 5개 → 0개
- [ ] 평균 파일 크기: 50KB → 20KB
- [ ] 빌드 시간: 53초 → 40초 이하
- [ ] 번들 크기: 1,693KB → 1,200KB 이하

### 정성적 지표
- [ ] 코드 리뷰 시간 단축
- [ ] 버그 수정 시간 단축
- [ ] 신규 기능 추가 속도 향상
- [ ] 팀 피드백 긍정적

---

## 🚨 위험 요소 및 대응

### 위험 1: 기능 손실
**대응**: 각 단계마다 수동 테스트, 빌드 확인

### 위험 2: Import 경로 오류
**대응**: TypeScript 컴파일러로 사전 검증

### 위험 3: 시간 부족
**대응**: Phase 단위로 우선순위 조정 가능

### 위험 4: Git 충돌
**대응**: 작은 단위 PR, 빠른 머지

---

## 📚 참고 자료

### 리팩토링 패턴
- Martin Fowler - Refactoring: Improving the Design of Existing Code
- Extract Function
- Extract Module
- Split Phase
- Move Function

### React 패턴
- Component Composition
- Custom Hooks
- Container/Presentational Pattern
- Feature-based Architecture

### 도구
- ESLint (max-lines rule)
- Prettier
- TypeScript strict mode
- Bundle Analyzer

---

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-10-20 | v1.0 | 초안 작성 |

---

## 💡 Note

이 문서는 살아있는 문서입니다. 리팩토링 진행 중 새로운 인사이트나 이슈가 발견되면 계속 업데이트합니다.

**원칙**: "완벽한 계획보다 점진적 개선"
