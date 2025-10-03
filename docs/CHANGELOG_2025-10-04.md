# 변경 이력 - 2025년 10월 4일

## 📋 개요
볼린저 밴드 조건 설정 UI 개선 및 Supabase 지표 동적 로드 시스템 구축

## 🎯 주요 변경사항

### 1. 볼린저 밴드 조건 설정 UI 개선

#### 볼린저 밴드 라인 선택 기능 추가
- **위치**: `src/components/StageBasedStrategy.tsx`
- **변경 내용**:
  - 상단/중간/하단 밴드 선택 UI 추가
  - `bollingerLine` 필드 추가 (`'bollinger_upper' | 'bollinger_middle' | 'bollinger_lower'`)
  - 볼린저 밴드 선택 시 기본 라인을 `bollinger_lower`로 자동 설정
  - FormControl 컴포넌트로 직관적인 선택 UI 구현

#### 볼린저 밴드 연산자 단순화
- **기존**:
  - 복잡한 15개 옵션 (price_above_upper, price_below_lower, band_squeeze 등)
- **변경 후**:
  - 4개 핵심 옵션으로 단순화
    - `price_above`: 종가가 위에 있음 (close > band)
    - `price_below`: 종가가 아래 있음 (close < band)
    - `cross_above`: 종가가 상향 돌파 (cross up)
    - `cross_below`: 종가가 하향 돌파 (cross down)

#### 조건 표시 레이블 개선
- **기능**: `getOperatorLabel` 함수 구현
- **효과**:
  - 볼린저 밴드 조건에 선택된 라인 정보 포함
  - 예: "상단밴드: 종가가 위에 있음", "하단밴드: 종가가 하향 돌파"
  - 가독성 및 사용자 경험 향상

### 2. Supabase 지표 동적 로드 시스템

#### indicatorService 구현
- **파일**: `src/services/indicatorService.ts` (신규 생성, 117 lines)
- **주요 기능**:
  ```typescript
  export async function getAvailableIndicators(): Promise<Indicator[]>
  ```
- **구현 내용**:
  - Supabase `indicators` 테이블에서 지표 목록 조회
  - `output_columns` 필드를 활용한 다중 출력 지표 처리
  - 에러 처리 및 로깅
  - 지표 타입별 분류 (trend, momentum, volatility, volume)

#### StrategyBuilder 통합
- **위치**: `src/components/StrategyBuilder.tsx`
- **변경 내용**:
  - `AVAILABLE_INDICATORS` 상수 제거 (하드코딩 제거)
  - `availableIndicators` state로 동적 관리
  - `useEffect`로 컴포넌트 마운트 시 지표 로드
  - 폴백 메커니즘: 로드 실패 시 기본 지표 제공 (RSI, MACD)
  - 로딩 상태 관리 (`indicatorsLoading`)

### 3. 조건 변환 로직 개선

#### conditionConverter 확장
- **파일**: `src/utils/conditionConverter.ts`
- **추가 기능**: 볼린저 밴드 특수 처리
- **변환 로직**:
  ```typescript
  // 예시
  price_above + bollinger_upper → { left: 'close', operator: '>', right: 'bollinger_upper' }
  price_below + bollinger_lower → { left: 'close', operator: '<', right: 'bollinger_lower' }
  cross_above + bollinger_middle → { left: 'close', operator: 'crossover', right: 'bollinger_middle' }
  cross_below + bollinger_upper → { left: 'close', operator: 'crossunder', right: 'bollinger_upper' }
  ```

#### 전략 저장 시 변환 적용
- **위치**: `StrategyBuilder.tsx` - `handleSaveStrategy` 함수
- **변경 내용**:
  - `buyStageStrategy`와 `sellStageStrategy`의 indicators를 conditions로 변환
  - `convertConditionToStandard` 함수 호출
  - `bollingerLine`, `macdLine`, `stochLine` 파라미터 전달

### 4. TypeScript 타입 정의 개선

#### Strategy 인터페이스 확장
- **파일**:
  - `src/components/BacktestRunner.tsx`
  - `src/components/StrategyBuilder.tsx`
- **추가 속성**:
  - `user_id?: string` (BacktestRunner)
  - `userId?: string` (StrategyBuilder)
- **목적**: 템플릿 필터링 (`!s.user_id`, `!s.userId`)

#### StageIndicator 인터페이스 확장
- **파일**: `src/components/StageBasedStrategy.tsx`
- **추가 필드**:
  ```typescript
  bollingerLine?: 'bollinger_upper' | 'bollinger_middle' | 'bollinger_lower'
  ```

### 5. 데이터베이스 스크립트

#### 새로운 SQL 스크립트 추가
1. **backend/fix_bollinger_columns.sql** (37 lines)
   - 볼린저 밴드 컬럼 수정 스크립트

2. **backend/verify_bollinger_columns.sql** (53 lines)
   - 볼린저 밴드 컬럼 검증 스크립트
   - `indicators` 테이블의 `output_columns` 확인

3. **backend/fix_macd_indicator.sql** (수정)
   - MACD 지표 output_columns 확인 쿼리로 변경
   - 기존 UPDATE 문 제거

### 6. UI/UX 개선

#### 조건 칩 표시 개선
- **위치**: `StageBasedStrategy.tsx`, `StrategyBuilder.tsx`
- **개선 내용**:
  - 볼린저 밴드 조건에 선택된 라인 레이블 표시
  - 예: "상단밴드: 종가가 상향 돌파"
  - Chip 컴포넌트에 사람이 읽기 쉬운 형식으로 표시

#### 볼린저 밴드 operator 선택 조건 분기
- **위치**: `StrategyBuilder.tsx`
- **변경 내용**:
  - 볼린저 밴드 선택 시 전용 연산자 옵션 표시
  - `getBollingerOperators()` 함수로 분리
  - 다른 지표와 명확히 구분

## 📊 변경 통계

### 파일 변경 요약
| 파일 | 추가 | 삭제 | 순변경 |
|------|------|------|--------|
| **신규 파일** | | | |
| src/services/indicatorService.ts | +117 | 0 | +117 |
| backend/fix_bollinger_columns.sql | +37 | 0 | +37 |
| backend/verify_bollinger_columns.sql | +53 | 0 | +53 |
| **수정 파일** | | | |
| src/components/StageBasedStrategy.tsx | +93 | -50 | +43 |
| src/components/StrategyBuilder.tsx | +202 | -153 | +49 |
| src/utils/conditionConverter.ts | +19 | 0 | +19 |
| src/components/BacktestRunner.tsx | +1 | 0 | +1 |
| backend/fix_macd_indicator.sql | +11 | -27 | -16 |
| src/components/common/RoadmapDialog.tsx | +75 | -35 | +40 |
| **총계** | **+608** | **-265** | **+343** |

### 커밋 이력
1. **347b06e** - `fix: Strategy 인터페이스에 user_id/userId 속성 추가`
   - Vercel 빌드 에러 수정
   - TypeScript 타입 오류 해결

2. **75b0161** - `feat: 볼린저 밴드 조건 설정 UI 개선 및 Supabase 지표 연동`
   - 주요 기능 구현
   - 7개 파일 변경 (+420, -139)

## 🔧 기술적 개선사항

### 1. 하드코딩 제거
- **이전**: `AVAILABLE_INDICATORS` 상수에 15개 지표 하드코딩
- **변경 후**: Supabase에서 동적으로 로드
- **장점**:
  - 지표 추가/수정 시 코드 변경 불필요
  - 데이터베이스에서 중앙 관리
  - 확장성 및 유지보수성 향상

### 2. 타입 안정성 강화
- Strategy 인터페이스에 user_id/userId 추가
- StageIndicator에 bollingerLine 필드 추가
- TypeScript 컴파일 에러 사전 방지

### 3. 사용자 경험 개선
- 볼린저 밴드 조건 설정 단순화 (15개 → 4개 옵션)
- 직관적인 라인 선택 UI
- 조건 칩에 명확한 레이블 표시

### 4. 코드 품질 향상
- 조건 변환 로직 중앙화 (conditionConverter)
- 에러 처리 및 폴백 메커니즘
- 명확한 함수 분리 (getOperatorLabel, getBollingerOperators)

## 🐛 버그 수정

### Vercel 빌드 에러
- **문제**: `Property 'user_id' does not exist on type 'Strategy'`
- **위치**:
  - `src/components/BacktestRunner.tsx:1629`
  - `src/components/StrategyBuilder.tsx:1245`
- **해결**: Strategy 인터페이스에 user_id/userId 속성 추가

### 볼린저 밴드 조건 표시 문제
- **문제**: 선택된 라인 정보가 표시되지 않음
- **해결**: getOperatorLabel 함수로 라인 정보 포함

## 📝 문서 업데이트

### RoadmapDialog 업데이트
- **파일**: `src/components/common/RoadmapDialog.tsx`
- **추가 내용**: Task #21 "볼린저 밴드 조건 설정 UI 개선"
- **세부사항**:
  - 볼린저 밴드 라인 선택 기능
  - Supabase 지표 동적 로드
  - 조건 변환 로직 개선
  - UI 개선 및 버그 수정
  - 데이터베이스 스크립트
- **ID 정리**: Task ID 중복 제거 및 재정렬 (1~27)

## 🚀 배포 상태

### Feature 브랜치
- **브랜치**: `feature/sell-or-logic-and-ui-improvements`
- **최신 커밋**: `347b06e`
- **상태**: Vercel 배포 성공

### 주요 개선 효과
1. ✅ TypeScript 빌드 에러 해결
2. ✅ Vercel 자동 배포 성공
3. ✅ 사용자 경험 개선
4. ✅ 코드 확장성 향상

## 🔜 다음 단계

### 권장 작업
1. **main 브랜치 병합**: feature 브랜치를 main에 병합
2. **테스트**: 볼린저 밴드 조건으로 전략 생성 및 백테스트
3. **문서화**: 사용자 가이드에 볼린저 밴드 조건 설정 방법 추가
4. **추가 지표**: 다른 다중 출력 지표도 유사하게 개선 (MACD, Stochastic 등)

---

**작성일**: 2025년 10월 4일
**작성자**: Claude Code
**브랜치**: feature/sell-or-logic-and-ui-improvements
