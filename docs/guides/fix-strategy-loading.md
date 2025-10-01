# 전략 로딩 문제 분석 및 수정

## 🚨 현재 문제
- 전략 불러오기 목록은 보임 ✅
- 전략 클릭 시 지표/설정이 적용되지 않음 ❌

## 🔍 문제 원인

### 저장 시 데이터 구조:
```typescript
const dataToSave = {
  name: strategy.name,
  description: strategy.description,
  config: parameters,  // <- 주요 설정이 config에 저장
  indicators: { list: strategy.indicators },  // <- indicators가 객체로 래핑
  entry_conditions: { buy: strategy.buyConditions },
  exit_conditions: { sell: strategy.sellConditions },
  risk_management: strategy.riskManagement,
  // ... 기타 설정
}
```

### 로드 시 기대하는 구조:
```typescript
const formattedStrategy = {
  indicators: strategyData.indicators || [],  // <- 배열을 기대하지만 객체가 옴
  buyConditions: strategyData.buyConditions || [],  // <- 없을 수 있음 (entry_conditions에 저장됨)
  sellConditions: strategyData.sellConditions || [],  // <- 없을 수 있음 (exit_conditions에 저장됨)
}
```

## ✅ 수정 방안

loadStrategy 함수를 수정하여 실제 저장된 데이터 구조에 맞게 파싱해야 함.

### 수정할 부분:
1. `indicators.list` → `indicators` 변환
2. `entry_conditions.buy` → `buyConditions` 변환
3. `exit_conditions.sell` → `sellConditions` 변환
4. `config` 안의 설정들 복원