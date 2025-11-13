-- ============================================================================
-- 기존 활성 전략에 할당 자금 설정
-- ============================================================================
-- 문제: 기존에 생성된 활성 전략들의 allocated_capital과 allocated_percent가 0으로 설정되어 있음
-- 해결: 각 전략에 적절한 할당 비율과 금액을 수동으로 설정
-- ============================================================================

-- 1단계: 현재 활성 전략 확인
SELECT
    id,
    name,
    allocated_capital,
    allocated_percent,
    auto_execute,
    is_active
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 2단계: 기존 활성 전략에 할당 자금 설정
-- ⚠️ 중요: 아래 UPDATE 문을 실행하기 전에 각 전략의 ID를 확인하고
--         적절한 할당 비율(%)과 금액(원)을 설정해야 합니다.

-- 예시 1: 특정 전략에 30% (3,000,000원) 할당
-- UPDATE strategies
-- SET
--     allocated_percent = 30,
--     allocated_capital = 3000000
-- WHERE id = '여기에-전략-UUID-입력';

-- 예시 2: 특정 전략에 50% (5,000,000원) 할당
-- UPDATE strategies
-- SET
--     allocated_percent = 50,
--     allocated_capital = 5000000
-- WHERE id = '여기에-전략-UUID-입력';

-- 3단계: 업데이트 후 확인
SELECT
    id,
    name,
    allocated_capital,
    allocated_percent,
    auto_execute,
    is_active
FROM strategies
WHERE auto_execute = true AND is_active = true;

-- 4단계: 전체 할당 현황 확인
SELECT * FROM strategy_capital_allocation;

-- ============================================================================
-- 참고: 간단한 UI를 통한 설정 방법
-- ============================================================================
-- 프론트엔드에서 기존 전략의 할당 자금을 수정할 수 있는 기능이 필요합니다.
-- 현재는 새 전략을 추가할 때만 할당 자금을 설정할 수 있습니다.
--
-- 임시 해결책:
-- 1. 기존 전략을 중지 (auto_execute = false)
-- 2. "새 자동매매 시작" 버튼으로 다시 활성화하면서 할당 자금 설정
-- 3. 또는 위의 SQL UPDATE 문을 직접 실행
-- ============================================================================
