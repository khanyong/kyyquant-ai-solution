-- =============================================
-- 전략(Strategy) 컬럼 정리 SQL
-- =============================================
-- 목적: is_active, auto_execute, auto_trade_enabled 컬럼을 적절하게 수정
-- 작성일: 2025-11-19
-- 참고: STRATEGY_COLUMNS_GUIDE.md
-- =============================================

-- =============================================
-- 1단계: 현재 상태 확인
-- =============================================

-- 1-1. 전체 전략 상태 확인
SELECT
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled,
    allocated_capital,
    allocated_percent,
    created_at
FROM strategies
ORDER BY is_active DESC, auto_execute DESC, created_at DESC;

-- 1-2. 컬럼별 통계
SELECT
    '전체 전략 수' as category,
    COUNT(*) as count
FROM strategies
UNION ALL
SELECT
    'is_active = true',
    COUNT(*)
FROM strategies
WHERE is_active = true
UNION ALL
SELECT
    'auto_execute = true',
    COUNT(*)
FROM strategies
WHERE auto_execute = true
UNION ALL
SELECT
    'auto_trade_enabled = true',
    COUNT(*)
FROM strategies
WHERE auto_trade_enabled = true
UNION ALL
SELECT
    '자동매매 활성화 (3개 모두 true)',
    COUNT(*)
FROM strategies
WHERE is_active = true
    AND auto_execute = true
    AND auto_trade_enabled = true;

-- 1-3. RPC 함수가 반환하는 전략 확인
SELECT * FROM get_active_strategies_with_universe();

-- =============================================
-- 2단계: 전략 정리 (권장 사항)
-- =============================================

-- 2-1. 모든 전략 비활성화 (초기화)
-- ⚠️ 주의: 이 쿼리를 실행하면 모든 자동매매가 중지됩니다!
UPDATE strategies
SET
    is_active = false,
    auto_execute = false,
    auto_trade_enabled = false,
    allocated_capital = 0,
    allocated_percent = 0,
    updated_at = NOW()
WHERE is_active = true;

-- 결과 확인
SELECT
    'is_active = true인 전략' as description,
    COUNT(*) as count
FROM strategies
WHERE is_active = true;

-- 2-2. 실제 사용할 전략만 활성화
-- 방법 1: 전략 이름으로 선택
UPDATE strategies
SET
    is_active = true,
    updated_at = NOW()
WHERE name = '[템플릿] 볼린저밴드'  -- ⭐ 실제 사용할 전략명으로 변경
    OR name = '[템플릿] RSI 역추세';  -- 여러 개 활성화 시 추가

-- 방법 2: 전략 ID로 선택 (더 정확함)
-- UPDATE strategies
-- SET
--     is_active = true,
--     updated_at = NOW()
-- WHERE id IN (
--     'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',  -- ⭐ 실제 전략 ID로 변경
--     'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'   -- 여러 개 활성화 시 추가
-- );

-- 결과 확인
SELECT
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled,
    created_at
FROM strategies
WHERE is_active = true;

-- =============================================
-- 3단계: 자동매매 활성화 (선택적)
-- =============================================

-- 3-1. 특정 전략의 자동매매 활성화
-- ⚠️ 주의: 이 쿼리는 실제로 자동매매를 시작합니다!
-- ⚠️ allocated_capital과 allocated_percent는 별도로 설정 필요

-- 방법 1: 전략 이름으로 활성화
UPDATE strategies
SET
    auto_execute = true,
    auto_trade_enabled = true,
    -- allocated_capital = 5000000,  -- ⭐ 실제 할당 금액으로 변경
    -- allocated_percent = 50,        -- ⭐ 실제 할당 비율로 변경
    updated_at = NOW()
WHERE name = '[템플릿] 볼린저밴드'  -- ⭐ 실제 전략명으로 변경
    AND is_active = true;

-- 방법 2: 전략 ID로 활성화 (더 정확함)
-- UPDATE strategies
-- SET
--     auto_execute = true,
--     auto_trade_enabled = true,
--     -- allocated_capital = 5000000,  -- ⭐ 실제 할당 금액으로 변경
--     -- allocated_percent = 50,        -- ⭐ 실제 할당 비율로 변경
--     updated_at = NOW()
-- WHERE id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  -- ⭐ 실제 전략 ID
--     AND is_active = true;

-- 3-2. 자동매매 활성화 결과 확인
SELECT
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled,
    allocated_capital,
    allocated_percent,
    created_at
FROM strategies
WHERE auto_execute = true
    OR auto_trade_enabled = true
ORDER BY created_at DESC;

-- 3-3. RPC 함수 결과 확인 (n8n이 모니터링할 전략)
SELECT
    strategy_id,
    strategy_name,
    filter_name,
    allocated_capital,
    allocated_percent
FROM get_active_strategies_with_universe();

-- =============================================
-- 4단계: 데이터 일관성 검증
-- =============================================

-- 4-1. 잘못된 상태의 전략 찾기
-- 패턴 1: auto_execute=true인데 is_active=false (불가능한 상태)
SELECT
    '❌ auto_execute=true but is_active=false' as issue,
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled
FROM strategies
WHERE auto_execute = true
    AND is_active = false;

-- 패턴 2: auto_trade_enabled=true인데 is_active=false (불가능한 상태)
SELECT
    '❌ auto_trade_enabled=true but is_active=false' as issue,
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled
FROM strategies
WHERE auto_trade_enabled = true
    AND is_active = false;

-- 패턴 3: auto_execute != auto_trade_enabled (불일치 상태)
SELECT
    '⚠️ auto_execute != auto_trade_enabled' as issue,
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled
FROM strategies
WHERE auto_execute != auto_trade_enabled;

-- 패턴 4: allocated_capital > 0인데 auto_execute=false (자금 회수 안 됨)
SELECT
    '⚠️ allocated_capital > 0 but auto_execute=false' as issue,
    id,
    name,
    is_active,
    auto_execute,
    allocated_capital,
    allocated_percent
FROM strategies
WHERE allocated_capital > 0
    AND auto_execute = false;

-- 4-2. 올바른 상태 패턴 확인
WITH strategy_status AS (
    SELECT
        CASE
            WHEN is_active = false
                AND auto_execute = false
                AND auto_trade_enabled = false
                AND allocated_capital = 0
                THEN '✅ 전략 비활성화 (Soft Deleted)'
            WHEN is_active = true
                AND auto_execute = false
                AND auto_trade_enabled = false
                AND allocated_capital = 0
                THEN '✅ 전략 활성 (자동매매 중지)'
            WHEN is_active = true
                AND auto_execute = true
                AND auto_trade_enabled = true
                AND allocated_capital > 0
                THEN '✅ 자동매매 실행 중'
            ELSE '❌ 비정상 상태'
        END as status
    FROM strategies
)
SELECT
    status,
    COUNT(*) as count
FROM strategy_status
GROUP BY status
ORDER BY status;

-- =============================================
-- 5단계: 안전 가드 (선택적)
-- =============================================

-- 5-1. 자동매매가 비활성화된 전략의 allocated_capital을 0으로 초기화
UPDATE strategies
SET
    allocated_capital = 0,
    allocated_percent = 0,
    updated_at = NOW()
WHERE auto_execute = false
    AND allocated_capital > 0;

-- 5-2. 비활성 전략의 auto_execute, auto_trade_enabled를 강제로 false로
UPDATE strategies
SET
    auto_execute = false,
    auto_trade_enabled = false,
    allocated_capital = 0,
    allocated_percent = 0,
    updated_at = NOW()
WHERE is_active = false
    AND (auto_execute = true OR auto_trade_enabled = true);

-- =============================================
-- 6단계: 최종 상태 확인
-- =============================================

-- 6-1. 전체 전략 요약
SELECT
    COUNT(*) as total_strategies,
    SUM(CASE WHEN is_active = true THEN 1 ELSE 0 END) as active_strategies,
    SUM(CASE WHEN auto_execute = true THEN 1 ELSE 0 END) as auto_execute_strategies,
    SUM(CASE WHEN auto_trade_enabled = true THEN 1 ELSE 0 END) as auto_trade_enabled_strategies,
    SUM(CASE WHEN allocated_capital > 0 THEN 1 ELSE 0 END) as allocated_strategies,
    COALESCE(SUM(allocated_capital), 0) as total_allocated_capital
FROM strategies;

-- 6-2. 전략 상태별 목록
SELECT
    id,
    name,
    is_active,
    auto_execute,
    auto_trade_enabled,
    allocated_capital,
    allocated_percent,
    CASE
        WHEN is_active = false THEN '🗑️ 삭제됨'
        WHEN auto_execute = true THEN '▶️ 자동매매 중'
        WHEN is_active = true THEN '⏸️ 대기 중'
        ELSE '❓ 알 수 없음'
    END as status_icon,
    created_at
FROM strategies
ORDER BY
    is_active DESC,
    auto_execute DESC,
    created_at DESC;

-- 6-3. RPC 함수 최종 확인 (n8n이 실제로 모니터링할 전략)
SELECT
    COUNT(*) as monitoring_strategies,
    STRING_AGG(strategy_name, ', ') as strategy_names,
    SUM(allocated_capital) as total_allocated
FROM get_active_strategies_with_universe();

-- =============================================
-- 7단계: 관련 테이블 정리 (선택적)
-- =============================================

-- 7-1. 비활성 전략의 strategy_universes 비활성화
UPDATE strategy_universes
SET
    is_active = false,
    updated_at = NOW()
WHERE strategy_id IN (
    SELECT id
    FROM strategies
    WHERE is_active = false
)
AND is_active = true;

-- 7-2. 자동매매 중지된 전략의 strategy_monitoring 데이터 삭제 (선택적)
-- ⚠️ 주의: 모니터링 히스토리가 삭제됩니다!
-- DELETE FROM strategy_monitoring
-- WHERE strategy_id IN (
--     SELECT id
--     FROM strategies
--     WHERE auto_execute = false
-- );

-- =============================================
-- 8단계: 롤백용 백업 (선택적)
-- =============================================

-- 8-1. 현재 상태 백업 테이블 생성
CREATE TABLE IF NOT EXISTS strategies_backup_20251119 AS
SELECT * FROM strategies;

-- 8-2. 백업 확인
SELECT COUNT(*) as backup_count FROM strategies_backup_20251119;

-- 8-3. 롤백이 필요한 경우 (비상시만 사용!)
-- UPDATE strategies
-- SET
--     is_active = b.is_active,
--     auto_execute = b.auto_execute,
--     auto_trade_enabled = b.auto_trade_enabled,
--     allocated_capital = b.allocated_capital,
--     allocated_percent = b.allocated_percent
-- FROM strategies_backup_20251119 b
-- WHERE strategies.id = b.id;

-- =============================================
-- 실행 순서 가이드
-- =============================================
/*
권장 실행 순서:

1. [필수] 1단계 실행 - 현재 상태 확인
   → is_active=true인 전략이 31개인지 확인

2. [선택] 8단계 실행 - 백업 생성
   → 안전을 위해 백업 테이블 생성

3. [필수] 2-1 실행 - 모든 전략 비활성화
   ⚠️ 주의: 모든 자동매매가 중지됩니다!

4. [필수] 2-2 실행 - 사용할 전략만 활성화
   → 전략 이름 또는 ID를 실제 값으로 수정 후 실행

5. [선택] 3-1 실행 - 자동매매 활성화
   → allocated_capital과 allocated_percent 주석 해제 후 실행
   → 또는 프론트엔드 UI에서 수동으로 설정

6. [필수] 4단계 실행 - 데이터 일관성 검증
   → 잘못된 상태가 없는지 확인

7. [선택] 5단계 실행 - 안전 가드
   → 불일치 데이터 자동 정리

8. [필수] 6단계 실행 - 최종 상태 확인
   → RPC 함수가 올바른 전략을 반환하는지 확인

9. [선택] 7단계 실행 - 관련 테이블 정리
   → strategy_universes도 함께 정리
*/

-- =============================================
-- 참고: 올바른 상태 패턴
-- =============================================
/*
상태 1: 전략 비활성화 (Soft Deleted)
  is_active = false
  auto_execute = false
  auto_trade_enabled = false
  allocated_capital = 0

상태 2: 전략 활성 (자동매매 중지)
  is_active = true
  auto_execute = false
  auto_trade_enabled = false
  allocated_capital = 0

상태 3: 자동매매 실행 중
  is_active = true
  auto_execute = true
  auto_trade_enabled = true
  allocated_capital > 0
  allocated_percent > 0
*/
