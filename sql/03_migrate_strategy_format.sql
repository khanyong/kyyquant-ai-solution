-- ============================================================
-- 전략 조건 형식 통일 마이그레이션
-- ============================================================
-- 목적: indicator/compareTo 형식 → left/right 형식으로 통일
-- 안전: 프리플라이트가 양쪽 형식 모두 지원하므로 점진적 마이그레이션 가능
-- ============================================================

-- ------------------------------------------------------------
-- 1. 현재 상태 분석
-- ------------------------------------------------------------

-- 형식 1 (left/right) 사용 전략 개수
SELECT
    'Format 1 (left/right)' as format_type,
    COUNT(*) as strategy_count
FROM strategies
WHERE
    config->'buyConditions' IS NOT NULL
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'buyConditions') AS cond
        WHERE cond ? 'left' AND cond ? 'right'
    );

-- 형식 2 (indicator/compareTo) 사용 전략 개수
SELECT
    'Format 2 (indicator/compareTo)' as format_type,
    COUNT(*) as strategy_count
FROM strategies
WHERE
    config->'buyConditions' IS NOT NULL
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'buyConditions') AS cond
        WHERE cond ? 'indicator'
    );


-- ------------------------------------------------------------
-- 2. 마이그레이션 함수
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION migrate_condition_format(condition jsonb)
RETURNS jsonb AS $$
DECLARE
    new_condition jsonb;
    operator_text text;
    left_value text;
    right_value text;
BEGIN
    -- 이미 left/right 형식이면 그대로 반환
    IF condition ? 'left' AND condition ? 'right' THEN
        RETURN condition;
    END IF;

    -- indicator/compareTo 형식인 경우 변환
    IF condition ? 'indicator' THEN
        operator_text := condition->>'operator';
        left_value := condition->>'indicator';

        -- compareTo가 있으면 right로
        IF condition ? 'compareTo' THEN
            right_value := condition->>'compareTo';

            -- operator 변환 (cross_above → crossover 등)
            operator_text := CASE operator_text
                WHEN 'cross_above' THEN 'crossover'
                WHEN 'cross_below' THEN 'crossunder'
                ELSE operator_text
            END;

            new_condition := jsonb_build_object(
                'left', left_value,
                'operator', operator_text,
                'right', right_value
            );

        -- value가 있으면 그대로 right로 (숫자)
        ELSIF condition ? 'value' THEN
            new_condition := jsonb_build_object(
                'left', left_value,
                'operator', operator_text,
                'right', condition->'value'  -- 숫자 그대로
            );

        ELSE
            -- indicator만 있고 compareTo/value 없으면 그대로
            RETURN condition;
        END IF;

        -- 추가 필드 보존 (id, type, combineWith 등)
        IF condition ? 'id' THEN
            new_condition := new_condition || jsonb_build_object('id', condition->'id');
        END IF;
        IF condition ? 'type' THEN
            new_condition := new_condition || jsonb_build_object('type', condition->'type');
        END IF;
        IF condition ? 'combineWith' THEN
            new_condition := new_condition || jsonb_build_object('combineWith', condition->'combineWith');
        END IF;

        RETURN new_condition;
    END IF;

    -- 그 외는 그대로
    RETURN condition;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- 3. 배열 전체 마이그레이션 함수
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION migrate_conditions_array(conditions jsonb)
RETURNS jsonb AS $$
DECLARE
    result jsonb := '[]'::jsonb;
    condition jsonb;
BEGIN
    IF conditions IS NULL OR jsonb_array_length(conditions) = 0 THEN
        RETURN conditions;
    END IF;

    FOR condition IN SELECT * FROM jsonb_array_elements(conditions)
    LOOP
        result := result || jsonb_build_array(migrate_condition_format(condition));
    END LOOP;

    RETURN result;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- 4. 마이그레이션 미리보기 (실행 전 확인)
-- ------------------------------------------------------------

SELECT
    s.id,
    s.name,
    s.config->'buyConditions' as old_buy_conditions,
    migrate_conditions_array(s.config->'buyConditions') as new_buy_conditions,
    s.config->'sellConditions' as old_sell_conditions,
    migrate_conditions_array(s.config->'sellConditions') as new_sell_conditions
FROM strategies s
WHERE
    s.config->'buyConditions' IS NOT NULL
    OR s.config->'sellConditions' IS NOT NULL
ORDER BY s.created_at DESC
LIMIT 5;


-- ------------------------------------------------------------
-- 5. 실제 마이그레이션 실행 (주의: 백업 후 실행!)
-- ------------------------------------------------------------

-- 5.1 백업 테이블 생성 (롤백용)
CREATE TABLE IF NOT EXISTS strategies_backup_before_format_migration AS
SELECT * FROM strategies;

-- 확인
SELECT COUNT(*) as backup_count FROM strategies_backup_before_format_migration;


-- 5.2 buyConditions 마이그레이션
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{buyConditions}',
        migrate_conditions_array(config->'buyConditions')
    ),
    updated_at = NOW()
WHERE
    config->'buyConditions' IS NOT NULL
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'buyConditions') AS cond
        WHERE cond ? 'indicator' AND NOT (cond ? 'left' AND cond ? 'right')
    );

-- 영향받은 행 수 확인
-- 출력: UPDATE X (X = 변경된 전략 수)


-- 5.3 sellConditions 마이그레이션
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{sellConditions}',
        migrate_conditions_array(config->'sellConditions')
    ),
    updated_at = NOW()
WHERE
    config->'sellConditions' IS NOT NULL
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(config->'sellConditions') AS cond
        WHERE cond ? 'indicator' AND NOT (cond ? 'left' AND cond ? 'right')
    );


-- ------------------------------------------------------------
-- 6. 마이그레이션 결과 확인
-- ------------------------------------------------------------

-- 6.1 형식별 전략 개수 (모두 Format 1이어야 함)
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM jsonb_array_elements(COALESCE(config->'buyConditions', '[]'::jsonb)) AS cond
            WHERE cond ? 'left' AND cond ? 'right'
        ) THEN 'Format 1 (left/right)'
        WHEN EXISTS (
            SELECT 1
            FROM jsonb_array_elements(COALESCE(config->'buyConditions', '[]'::jsonb)) AS cond
            WHERE cond ? 'indicator'
        ) THEN 'Format 2 (indicator/compareTo)'
        ELSE 'Empty or Other'
    END as format_type,
    COUNT(*) as count
FROM strategies
WHERE config->'buyConditions' IS NOT NULL
GROUP BY format_type;


-- 6.2 샘플 전략 확인 (변환 결과)
SELECT
    id,
    name,
    config->'buyConditions' as buy_conditions,
    config->'sellConditions' as sell_conditions
FROM strategies
WHERE name LIKE '[템플릿]%'
ORDER BY created_at DESC
LIMIT 3;


-- ------------------------------------------------------------
-- 7. 롤백 (문제 발생 시)
-- ------------------------------------------------------------

-- 백업에서 복원
/*
TRUNCATE TABLE strategies;
INSERT INTO strategies SELECT * FROM strategies_backup_before_format_migration;

-- 확인
SELECT COUNT(*) FROM strategies;
*/


-- ------------------------------------------------------------
-- 8. 정리 (마이그레이션 성공 확인 후)
-- ------------------------------------------------------------

-- 마이그레이션 함수 제거 (더 이상 필요 없음)
/*
DROP FUNCTION IF EXISTS migrate_condition_format(jsonb);
DROP FUNCTION IF EXISTS migrate_conditions_array(jsonb);

-- 백업 테이블 제거 (1주일 후)
DROP TABLE IF EXISTS strategies_backup_before_format_migration;
*/


-- ------------------------------------------------------------
-- 9. 최종 검증
-- ------------------------------------------------------------

DO $$
DECLARE
    format2_count INT;
BEGIN
    -- Format 2 형식이 남아있는지 확인
    SELECT COUNT(*) INTO format2_count
    FROM strategies
    WHERE
        (config->'buyConditions' IS NOT NULL AND EXISTS (
            SELECT 1
            FROM jsonb_array_elements(config->'buyConditions') AS cond
            WHERE cond ? 'indicator' AND NOT (cond ? 'left' AND cond ? 'right')
        ))
        OR
        (config->'sellConditions' IS NOT NULL AND EXISTS (
            SELECT 1
            FROM jsonb_array_elements(config->'sellConditions') AS cond
            WHERE cond ? 'indicator' AND NOT (cond ? 'left' AND cond ? 'right')
        ));

    IF format2_count > 0 THEN
        RAISE NOTICE '⚠️  Warning: % strategies still use Format 2', format2_count;
    ELSE
        RAISE NOTICE '✅ All strategies migrated to Format 1 (left/right)';
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'Migration Summary:';
    RAISE NOTICE '  - Backup table: strategies_backup_before_format_migration';
    RAISE NOTICE '  - Total strategies: %', (SELECT COUNT(*) FROM strategies);
    RAISE NOTICE '  - Migrated strategies: %', (SELECT COUNT(*) FROM strategies WHERE updated_at > NOW() - INTERVAL '5 minutes');
END $$;