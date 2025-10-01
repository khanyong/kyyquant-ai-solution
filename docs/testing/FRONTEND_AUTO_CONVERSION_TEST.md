# 프론트엔드 자동 변환 테스트 가이드

## ✅ 빌드 완료
- TypeScript 컴파일 성공
- Vite 번들링 완료 (1,484KB → 456KB gzipped)
- 모든 컴포넌트 타입 체크 통과

## 🧪 자동 변환 검증 방법

### 1. 전략 생성 테스트 (StrategyBuilder)

1. **브라우저에서 StrategyBuilder 열기**
   - URL: `http://localhost:3000/strategy-builder`

2. **새 전략 생성**
   - 지표 추가: SMA(20), SMA(50)
   - 매수 조건: SMA(20) cross_above SMA(50)
   - 매도 조건: SMA(20) cross_below SMA(50)

3. **저장 버튼 클릭 후 콘솔 확인**
   ```javascript
   // 콘솔에 다음 메시지가 표시되어야 함:
   [StrategyBuilder] Converted to standard format: {
     buyConditions: [
       { left: "sma_20", operator: "crossover", right: "sma_50" }
     ],
     sellConditions: [
       { left: "sma_20", operator: "crossunder", right: "sma_50" }
     ]
   }
   ```

4. **Supabase에서 확인**
   ```sql
   SELECT
     name,
     config->'buyConditions' as buy_conditions,
     config->'sellConditions' as sell_conditions
   FROM strategies
   WHERE name = '방금 생성한 전략명'
   ORDER BY created_at DESC
   LIMIT 1;
   ```

   **기대 결과**:
   ```json
   {
     "buyConditions": [
       {"left": "sma_20", "operator": "crossover", "right": "sma_50"}
     ]
   }
   ```

### 2. 백엔드 프리플라이트 테스트

1. **NAS 서버 배포 후 백테스트 실행**
   ```bash
   curl -X POST http://192.168.50.150:8001/api/backtest/run \
     -H "Content-Type: application/json" \
     -d '{
       "strategy_id": "새로_생성한_전략_UUID",
       "stock_codes": ["005930"],
       "start_date": "2024-01-01",
       "end_date": "2024-12-31",
       "initial_capital": 10000000
     }'
   ```

2. **프리플라이트 검증 로그 확인**
   ```bash
   docker logs backend_container | grep "Preflight"
   # 기대 출력:
   # [API] Running preflight validation...
   # [Preflight] Validating strategy config...
   # [Preflight] Format detected: standard (left/right)
   # [Preflight] Required columns: ['sma_20', 'sma_50', 'close']
   # [API] Preflight passed: 0 warnings, 2 info
   ```

### 3. 레거시 형식 변환 테스트

**기존 전략 편집 시나리오**:
1. Supabase의 기존 전략 (indicator/compareTo 형식) 로드
2. StrategyBuilder에서 편집
3. 저장 시 자동으로 left/right 형식으로 변환

**검증 SQL**:
```sql
-- 변환 전후 비교
SELECT
  id, name,
  config->'buyConditions' as conditions_before,
  updated_at
FROM strategies
WHERE id = '기존_전략_UUID';
```

## 📋 변환 규칙 확인

### 연산자 매핑
| 구 형식 | 새 형식 |
|---------|---------|
| `cross_above` | `crossover` |
| `cross_below` | `crossunder` |
| `=` | `==` |

### 지표명 정규화
| 입력 | 출력 |
|------|------|
| `MA_20` | `sma_20` |
| `PRICE` | `close` |
| `RSI` | `rsi` |

## ⚠️ 알려진 이슈

1. **템플릿 전략은 아직 구 형식 사용**
   - `sql/04_reset_strategies_with_standard_templates.sql` 실행 필요
   - 모든 템플릿을 새 형식으로 재생성

2. **백엔드 NAS 배포 필요**
   - 현재 로컬에서만 테스트 완료
   - NAS 서버에 다음 파일 업로드 필요:
     - `backend/backtest/preflight.py` (양쪽 형식 지원)
     - `backend/indicators/calculator.py` (DB 전용 모드)

## 🚀 배포 체크리스트

- [x] 프론트엔드 빌드 성공
- [x] conditionConverter.ts 생성
- [x] StrategyBuilder.tsx 수정
- [x] BacktestRunner.tsx 타입 에러 수정
- [ ] NAS 서버 배포
- [ ] Supabase 템플릿 재생성
- [ ] 엔드투엔드 테스트

## 🔄 다음 단계

1. **NAS 배포**
   ```bash
   # deploy_to_nas.sh 스크립트 사용
   bash deploy_to_nas.sh
   ```

2. **Supabase 템플릿 재생성**
   ```bash
   # Supabase SQL Editor에서 실행
   psql -f sql/04_reset_strategies_with_standard_templates.sql
   ```

3. **프로덕션 검증**
   - 새 전략 생성 → 저장 → 백테스트
   - 기존 전략 편집 → 저장 → 백테스트
   - 템플릿 전략 사용 → 백테스트
