# 자동매매 시스템 DB 마이그레이션

## 📋 개요

이 마이그레이션은 자동매매 시스템의 "매수 대기 종목" 및 "대기중인 주문" 기능을 구현하기 위한 데이터베이스 스키마 변경입니다.

## 🎯 주요 변경사항

### 1. 새 테이블: `strategy_monitoring`
- **목적**: 조건 근접도 추적 (매수 대기 종목 관리)
- **주요 필드**:
  - `condition_match_score`: 조건 충족도 점수 (0-100)
  - `conditions_met`: 각 조건별 충족 상태 (JSONB)
  - `is_near_entry`: 매수 조건 80% 이상 충족 여부

### 2. `orders` 테이블 수정
- **추가 컬럼**:
  - `auto_cancel_at`: 자동 취소 예정 시각
  - `cancel_after_minutes`: 주문 후 자동 취소까지 분 수 (기본 30분)
  - `cancellation_reason`: 취소 사유
  - `original_order_price`: 최초 주문 가격 (호가 변동 감지용)

### 3. `trading_signals` 테이블 수정
- **추가 컬럼**:
  - `order_id`: 생성된 주문 ID
  - `signal_status`: 신호 상태 (PENDING, ORDERED, CANCELLED, EXECUTED)

## 📝 실행 순서

### Supabase SQL Editor에서 실행

1. **01_create_strategy_monitoring_table.sql**
   - strategy_monitoring 테이블 생성
   - 인덱스 및 트리거 설정

2. **02_alter_orders_table.sql**
   - orders 테이블에 자동 취소 관련 컬럼 추가
   - 기존 데이터 업데이트

3. **03_alter_trading_signals_table.sql**
   - trading_signals 테이블에 주문 추적 컬럼 추가
   - 제약 조건 설정

4. **04_create_sample_data.sql** (선택사항)
   - 테스트용 샘플 데이터 생성
   - ⚠️ 실제 데이터가 있으면 건너뛰세요

5. **99_verify_schema.sql**
   - 모든 변경사항이 정상 적용되었는지 검증
   - 필수 실행!

## ✅ 검증 체크리스트

- [ ] strategy_monitoring 테이블 생성 확인
- [ ] strategy_monitoring 인덱스 3개 생성 확인
- [ ] orders 테이블에 4개 컬럼 추가 확인
- [ ] orders 기존 데이터 업데이트 확인 (PENDING, PARTIAL 주문)
- [ ] trading_signals 테이블에 2개 컬럼 추가 확인
- [ ] trading_signals check 제약 조건 확인
- [ ] 모든 인덱스 정상 생성 확인
- [ ] 99_verify_schema.sql 실행 결과 확인

## 🔧 롤백 방법 (필요시)

```sql
-- strategy_monitoring 테이블 삭제
DROP TABLE IF EXISTS strategy_monitoring CASCADE;

-- orders 테이블 컬럼 제거
ALTER TABLE orders
DROP COLUMN IF EXISTS auto_cancel_at,
DROP COLUMN IF EXISTS cancel_after_minutes,
DROP COLUMN IF EXISTS cancellation_reason,
DROP COLUMN IF EXISTS original_order_price;

-- trading_signals 테이블 컬럼 제거
ALTER TABLE trading_signals
DROP CONSTRAINT IF EXISTS check_signal_status,
DROP COLUMN IF EXISTS order_id,
DROP COLUMN IF EXISTS signal_status;
```

## 📞 문제 발생 시

에러가 발생하면:
1. 에러 메시지 전체를 복사
2. 어느 단계에서 발생했는지 확인
3. 해당 SQL 파일 번호와 함께 문의

## 다음 단계

Phase 1 완료 후:
- **Phase 2**: n8n 워크플로우 구현
- **Phase 3**: 프론트엔드 코드 수정 (StrategyCard.tsx 등)
