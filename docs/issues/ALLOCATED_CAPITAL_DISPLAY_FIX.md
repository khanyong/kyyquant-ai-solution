# 할당 자금 표시 문제 해결

## 📋 문제 상황

사용자가 보고한 문제:
- 자동매매 탭의 "활성 전략별 현황"에 2개의 활성 전략이 있음
- 각 전략에 할당금액이 설정되어 있어야 하는데 프론트엔드에서 보이지 않음

## 🔍 원인 분석

### 1. 코드 검증
- [AutoTradingPanelV2.tsx:84-85](src/components/trading/AutoTradingPanelV2.tsx#L84-L85): 데이터 로드 정상
- [AutoTradingPanelV2.tsx:249-250](src/components/trading/AutoTradingPanelV2.tsx#L249-L250): props 전달 정상
- [StrategyCard.tsx:225](src/components/trading/StrategyCard.tsx#L225): 렌더링 코드 정상

### 2. 실제 원인
기존에 생성된 활성 전략들의 `allocated_capital`과 `allocated_percent` 컬럼 값이 **0 또는 NULL**로 설정되어 있음.

**왜 이런 일이 발생했나?**
1. `supabase/migrations/add_strategy_capital_allocation.sql` 마이그레이션이 컬럼을 추가함
2. 새로 추가된 컬럼의 기본값은 `DEFAULT 0`
3. 기존에 생성된 전략들은 자동으로 0으로 설정됨
4. 새 전략을 추가할 때만 할당 자금을 설정할 수 있었고, 기존 전략을 수정하는 기능이 없었음

### 3. StrategyCard는 값을 제대로 표시함
```typescript
// StrategyCard.tsx:225
{formatCurrency(allocatedCapital)}원
```
- 코드는 정상 작동
- `allocatedCapital`이 0이면 "0원"으로 표시됨
- 값이 없어서 안 보이는 것이 아니라, 값이 0이어서 의미가 없는 것

## ✅ 해결 방법

### 새로 추가된 기능: 전략 수정 다이얼로그

#### 1. 새 파일: `EditStrategyDialog.tsx`
기존 활성 전략의 할당 자금을 수정할 수 있는 다이얼로그 컴포넌트 생성.

**기능**:
- 전략명 표시 (읽기 전용)
- 할당 비율(%) 수정
- 할당 금액(원) 수정
- 유효성 검증 (비율 > 0)
- Supabase 업데이트

#### 2. 수정된 파일: `AutoTradingPanelV2.tsx`
기존의 `handleEditStrategy` 함수를 구현하여 수정 다이얼로그를 열도록 변경.

**변경사항**:
```typescript
// Before
const handleEditStrategy = (strategyId: string) => {
  // TODO: 전략 수정 다이얼로그 열기
  alert('전략 수정 기능은 준비 중입니다.')
}

// After
const handleEditStrategy = (strategyId: string) => {
  const strategy = activeStrategies.find(s => s.strategy_id === strategyId)
  if (strategy) {
    setEditingStrategy(strategy)
    setShowEditDialog(true)
  }
}
```

## 🎯 사용 방법

### 프론트엔드에서 수정하기 (권장)

1. **자동매매 포트폴리오** 탭으로 이동
2. 할당 자금이 표시되지 않는 전략 카드에서 **"수정"** 버튼 클릭
3. **"전략 수정"** 다이얼로그가 열림
4. 할당 비율(%) 및 할당 금액(원) 입력
   - 예: 30% / 3,000,000원
   - 예: 50% / 5,000,000원
5. **"저장"** 버튼 클릭
6. 페이지가 자동 새로고침되며 할당 자금이 표시됨

### SQL로 직접 수정하기 (대안)

`supabase/update_existing_strategy_allocations.sql` 파일 참조:

```sql
-- 1단계: 현재 활성 전략 ID 확인
SELECT id, name FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 2단계: 각 전략에 할당 자금 설정
UPDATE strategies
SET
    allocated_percent = 30,
    allocated_capital = 3000000
WHERE id = '전략-UUID-여기에-입력';

-- 3단계: 업데이트 확인
SELECT id, name, allocated_capital, allocated_percent
FROM strategies
WHERE auto_execute = true AND is_active = true;
```

## 📊 예상 결과

### 수정 전
```
전략 A
━━━━━━━━━━━━━━━━━━━━━━
할당금액: 0원          ❌ 의미 없음
투자 중: 1,500,000원
대기금액: -1,500,000원  ❌ 음수!
```

### 수정 후
```
전략 A
━━━━━━━━━━━━━━━━━━━━━━
할당금액: 3,000,000원   ✅ 명확함
투자 중: 1,500,000원
대기금액: 1,500,000원   ✅ 정상
[진행률 바: 50%]
```

## 🔄 데이터 흐름

```
1. 사용자가 "수정" 버튼 클릭
   ↓
2. EditStrategyDialog 열림
   - 현재 allocated_capital, allocated_percent 표시
   ↓
3. 사용자가 새 값 입력
   ↓
4. "저장" 버튼 클릭
   ↓
5. Supabase UPDATE:
   UPDATE strategies
   SET allocated_capital = ?, allocated_percent = ?
   WHERE id = ?
   ↓
6. 성공 시:
   - loadData() 호출
   - 전략 목록 새로고침
   - 다이얼로그 닫힘
   ↓
7. StrategyCard에 업데이트된 값 표시
```

## 📝 참고사항

### 마이그레이션 파일
- `supabase/migrations/add_strategy_capital_allocation.sql`: 컬럼 추가
- 이미 적용되어 있어야 함 (기본값 0으로 설정)

### 관련 컴포넌트
- `AddStrategyDialog.tsx`: 새 전략 추가 시 할당 자금 설정
- `EditStrategyDialog.tsx`: 기존 전략 수정 (새로 추가됨)
- `StrategyCard.tsx`: 할당 자금 표시

### 제약 조건
데이터베이스 레벨에서 유효성 검증:
- `allocated_percent`: 0 ~ 100% 범위
- `allocated_capital`: 0 이상

## 🎉 완료!

이제 사용자는:
1. ✅ 기존 활성 전략의 할당 자금을 쉽게 수정할 수 있음
2. ✅ 전략 카드에 할당금액이 정확히 표시됨
3. ✅ 대기금액이 올바르게 계산됨 (할당금액 - 투자금액)
4. ✅ 진행률 바가 정상 작동함
