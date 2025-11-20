# 시장 가격 데이터 검증 수정

## 문제점

`kw_price_current` 테이블에 `current_price = 0`, `change_rate = -100%` 인 잘못된 데이터가 저장되고 있습니다.

### 원인
1. **n8n 워크플로우 v38의 장시간 체크 비활성화**: 테스트 모드로 항상 실행되어 장외 시간에도 데이터 저장
2. **가격 검증 로직 없음**: API에서 받은 0원 데이터를 그대로 저장
3. **Kiwoom Mock API 동작**: 장외 시간에 sel_fpr_bid = 0, buy_fpr_bid = 0 반환

## 해결 방법

### 1. n8n 워크플로우 수정 (`auto-trading-with-capital-validation-v38-fixed.json`)

**변경사항:**
- ✅ 장시간 체크 활성화 (09:00~15:30, 월~금)
- ✅ 가격 검증 로직 추가
  - `estimatedPrice === 0` → 저장 스킵
  - `selPrice === 0 || buyPrice === 0` → 저장 스킵
  - `changeRate === -100 || changeRate < -50` → 저장 스킵

### 2. 기존 잘못된 데이터 정리

실행할 SQL 파일: `clean_invalid_price_data.sql`

```sql
-- current_price가 0인 데이터 삭제
DELETE FROM kw_price_current
WHERE current_price::numeric = 0 OR current_price IS NULL;
```

## 배포 절차

### 1단계: 기존 잘못된 데이터 정리
```bash
# Supabase SQL Editor에서 실행
# 또는
psql -h db.hznkyaomtrpzcayayayh.supabase.co -U postgres -d postgres -f supabase/clean_invalid_price_data.sql
```

### 2단계: n8n 워크플로우 업데이트
1. n8n에서 "자동매매 모니터링 v38 (Stock Name Fix)" 워크플로우 비활성화
2. `auto-trading-with-capital-validation-v38-fixed.json` 임포트
3. 새 워크플로우 활성화

### 3단계: 동작 확인
- 장외 시간(15:30 이후)에는 데이터가 저장되지 않아야 함
- 장중 시간에만 유효한 가격 데이터 저장
- `kw_price_current` 테이블에서 `current_price > 0` 확인

## 검증 쿼리

```sql
-- 현재 데이터 상태 확인
SELECT
  COUNT(*) as total_count,
  COUNT(CASE WHEN current_price::numeric = 0 THEN 1 END) as zero_price_count,
  COUNT(CASE WHEN current_price::numeric > 0 THEN 1 END) as valid_price_count,
  MAX(updated_at) as last_update
FROM kw_price_current;

-- 최근 업데이트 데이터 샘플
SELECT
  stock_code,
  stock_name,
  current_price,
  change_rate,
  updated_at
FROM kw_price_current
WHERE current_price::numeric > 0
ORDER BY updated_at DESC
LIMIT 10;
```

## 주요 개선사항

### v38 (기존) vs v38-fixed (수정)

| 항목 | v38 (기존) | v38-fixed (수정) |
|------|-----------|-----------------|
| 장시간 체크 | `1 === 1` (항상 true) | `hour >= 9 && hour <= 15 && day >= 1 && day <= 5` |
| 가격 검증 | ❌ 없음 | ✅ 0원/비정상 등락률 스킵 |
| 데이터 품질 | ⚠️ 잘못된 데이터 저장 | ✅ 유효한 데이터만 저장 |

## 예상 효과

- ✅ 장외 시간에 잘못된 데이터 저장 방지
- ✅ MarketMonitor UI에 정상 가격 데이터 표시
- ✅ 시스템 신뢰성 향상
