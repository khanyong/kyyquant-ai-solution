# n8n 워크플로우 동작 확인 가이드

## 1. n8n UI 접속
- URL: `http://nas-server:5678` (또는 설정된 n8n 주소)

## 2. 워크플로우 상태 확인

### ✅ 확인 항목:
1. **workflow-v7-1-enhanced-with-exit-monitoring** 활성화 여부
   - Active 토글이 켜져 있어야 함 (초록색)

2. **기존 workflow-v7-1** 비활성화 여부
   - Active 토글이 꺼져 있어야 함 (회색)

## 3. 실행 로그 확인

### 워크플로우 실행 확인:
1. 워크플로우 클릭
2. 우측 상단 "Executions" 탭 클릭
3. 최근 실행 내역 확인

### ✅ 정상 동작 시그널:
```
✓ Every 1 Minute
✓ Get Active Strategies
✓ Split Strategies
✓ Prepare Monitoring Tasks
✓ If Exit Query (TRUE/FALSE 분기)
✓ Get Held Stocks (EXIT 모니터링 시)
✓ Upsert to Strategy Monitoring
```

### ❌ 에러 확인:
- 빨간색 X 표시가 있는 노드
- Error 메시지 확인

## 4. strategy_monitoring 테이블 업데이트 확인

Supabase SQL Editor에서 실행:
```sql
-- 최근 1분 이내 업데이트된 데이터 확인
SELECT
    stock_code,
    condition_match_score,
    exit_condition_match_score,
    is_held,
    updated_at
FROM strategy_monitoring
WHERE updated_at > NOW() - INTERVAL '1 minute'
ORDER BY updated_at DESC;
```

### ✅ 정상 동작 시:
- 매 1분마다 새로운 레코드가 업데이트됨
- `exit_condition_match_score`가 NULL이 아닌 값 (보유 종목의 경우)
- `is_held`가 true/false로 정확히 설정됨

## 5. 매도 대기 종목 확인

```sql
-- 매도 조건 80% 이상 충족한 보유 종목 확인
SELECT
    stock_code,
    stock_name,
    exit_condition_match_score,
    is_held,
    exit_conditions_met
FROM strategy_monitoring
WHERE is_held = true
  AND exit_condition_match_score >= 80
  AND exit_condition_match_score < 100
ORDER BY exit_condition_match_score DESC;
```

### ✅ 정상 동작 시:
- 보유 종목 중 매도 조건에 근접한 종목이 표시됨
- 비보유 종목은 절대 나타나지 않음
