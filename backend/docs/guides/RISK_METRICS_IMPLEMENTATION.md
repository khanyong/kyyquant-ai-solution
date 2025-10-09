# 위험조정 성과지표 구현 가이드

## 📋 개요

백테스트 결과에 3가지 위험조정 성과지표(샤프, 소르티노, 트레이너 비율)를 추가했습니다.

- **작성일**: 2025-10-08
- **버전**: 1.0
- **관련 이슈**: 샤프비율이 계산되지 않는 문제

---

## 📊 구현된 지표

### 1. 샤프 비율 (Sharpe Ratio)
```
샤프 비율 = (평균 수익률 - 무위험 이자율) / 전체 변동성
```
- **의미**: 위험(변동성) 대비 초과 수익
- **높을수록 좋음**: 동일한 위험에서 더 높은 수익
- **일반적 기준**:
  - < 0: 무위험 자산보다 낮음
  - 0~1: 보통
  - 1~2: 좋음
  - 2~3: 매우 좋음
  - > 3: 탁월함

### 2. 소르티노 비율 (Sortino Ratio)
```
소르티노 비율 = (평균 수익률 - 무위험 이자율) / 하방 변동성
```
- **의미**: 하방 위험(손실만) 대비 초과 수익
- **샤프 비율과 차이**: 상승 변동성은 제외하고 하락만 위험으로 간주
- **일반적으로 샤프 비율보다 높음**: 손실 변동성만 고려하므로

### 3. 트레이너 비율 (Treynor Ratio)
```
트레이너 비율 = (평균 수익률 - 무위험 이자율) / 베타
```
- **의미**: 시장 위험(베타) 대비 초과 수익
- **현재 구현**: 베타=1.0으로 가정 (시장과 동일한 변동성)
- **TODO**: KOSPI 지수 데이터 추가하여 실제 베타 계산 필요

---

## 🔧 구현 상세

### 1. 데이터베이스 (Supabase)

#### 테이블 스키마 수정
**파일**: [supabase/02-dependent-tables.sql](../../../supabase/02-dependent-tables.sql)

```sql
CREATE TABLE IF NOT EXISTS backtest_results (
    -- ... 기존 컬럼 ...
    sharpe_ratio DECIMAL(10, 4),   -- 샤프 비율
    sortino_ratio DECIMAL(10, 4),  -- 소르티노 비율
    treynor_ratio DECIMAL(10, 4),  -- 트레이너 비율
    -- ... 나머지 컬럼 ...
);
```

#### 마이그레이션 스크립트
**파일**: [supabase/migrations/add_risk_metrics.sql](../../../supabase/migrations/add_risk_metrics.sql)

```bash
# Supabase에서 실행
psql -h your-db-host -U postgres -d postgres < supabase/migrations/add_risk_metrics.sql
```

---

### 2. 백엔드 계산 로직

#### Engine 수정
**파일**: [backend/backtest/engine.py:519-589](../../../backend/backtest/engine.py#L519-L589)

**주요 로직**:
```python
# 일별 수익률 계산
daily_returns = []
for i in range(1, len(daily_values)):
    prev_value = daily_values[i-1]['total_value']
    curr_value = daily_values[i]['total_value']
    if prev_value > 0:
        daily_return = (curr_value - prev_value) / prev_value
        daily_returns.append(daily_return)

# 무위험 이자율 (연 3% 가정)
risk_free_rate_daily = 0.03 / 252
excess_return = avg_return - risk_free_rate_daily

# 1. 샤프 비율
sharpe_ratio = (excess_return / std_return) * np.sqrt(252)

# 2. 소르티노 비율 (하방 변동성만 사용)
downside_returns = [r for r in daily_returns if r < risk_free_rate_daily]
downside_std = np.std(downside_returns, ddof=1)
sortino_ratio = (excess_return / downside_std) * np.sqrt(252)

# 3. 트레이너 비율 (베타=1.0 가정)
assumed_beta = 1.0
treynor_ratio = (excess_return * 252) / assumed_beta
```

**연율화 (Annualization)**:
- 일별 수익률 → 연간 수익률: `× 252` (거래일 기준)
- 일별 변동성 → 연간 변동성: `× √252`

---

### 3. API 응답

#### Backtest API 수정
**파일**: [backend/api/backtest.py:162-164, 188-190](../../../backend/api/backtest.py#L162-L164)

```python
api_response = {
    'summary': {
        # ... 기존 필드 ...
        'sharpe_ratio': result.get('sharpe_ratio'),
        'sortino_ratio': result.get('sortino_ratio'),
        'treynor_ratio': result.get('treynor_ratio'),
    },
    # 전체 데이터에도 포함
    'sharpe_ratio': result.get('sharpe_ratio'),
    'sortino_ratio': result.get('sortino_ratio'),
    'treynor_ratio': result.get('treynor_ratio'),
}
```

---

### 4. 프론트엔드 표시

#### UI 컴포넌트 수정
**파일**: [src/components/backtest/BacktestResultViewer.tsx:495-547](../../../src/components/backtest/BacktestResultViewer.tsx#L495-L547)

**변경 사항**:
- 기존: 샤프 비율 1개 카드
- 수정: 샤프, 소르티노, 트레이너 비율 3개 카드

```tsx
{/* 샤프 비율 */}
<Grid item xs={12} md={3}>
  <Card>
    <CardContent>
      <Typography color="textSecondary" variant="body2">
        샤프 비율
      </Typography>
      <Typography variant="h4">
        {result.sharpe_ratio?.toFixed(2) || 'N/A'}
      </Typography>
      <Typography variant="caption" color="textSecondary">
        위험 대비 수익
      </Typography>
    </CardContent>
  </Card>
</Grid>

{/* 소르티노 비율 */}
<Grid item xs={12} md={3}>
  <!-- 동일한 구조 -->
</Grid>

{/* 트레이너 비율 */}
<Grid item xs={12} md={3}>
  <!-- 동일한 구조 -->
</Grid>
```

#### TypeScript 인터페이스
**파일**:
- [src/components/backtest/BacktestResultViewer.tsx:88-90](../../../src/components/backtest/BacktestResultViewer.tsx#L88-L90)
- [src/lib/supabase.ts:104-106](../../../src/lib/supabase.ts#L104-L106)

```typescript
interface BacktestResult {
  // ... 기존 필드 ...
  sharpe_ratio?: number;   // 샤프 비율
  sortino_ratio?: number;  // 소르티노 비율
  treynor_ratio?: number;  // 트레이너 비율
}
```

---

## 📝 배포 체크리스트

### 1. 데이터베이스 마이그레이션
```bash
# ✅ Supabase에서 마이그레이션 실행
psql < supabase/migrations/add_risk_metrics.sql

# 또는 Supabase Dashboard에서 SQL Editor로 실행
```

### 2. 백엔드 재시작
```bash
# ✅ NAS 서버에서 백엔드 재시작
cd /path/to/auto_stock/backend
pkill -f "uvicorn.*api.main:app"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 프론트엔드 재빌드 (선택)
```bash
# TypeScript 타입 변경만 있으므로 HMR로 자동 반영됨
# 필요시에만 재빌드
npm run build
```

### 4. 테스트
- [ ] 백테스트 실행
- [ ] 결과 화면에서 3가지 지수 확인
- [ ] Supabase 테이블에 데이터 저장 확인

---

## 🧪 테스트 예시

### 백테스트 실행 후 콘솔 로그
```
[Engine] Backtest completed successfully
[Engine] Results: Total trades: 25, Final capital: 11,095,000, Return: 10.95%
[Engine] Risk Metrics: Sharpe=1.23, Sortino=1.67, Treynor=0.08
```

### 기대 결과
- **샤프 비율**: 1.23 (좋음)
- **소르티노 비율**: 1.67 (샤프보다 높음 - 정상)
- **트레이너 비율**: 0.08 (베타=1.0 기준)

---

## ⚠️ 주의사항

### 1. 무위험 이자율
- **현재 설정**: 연 3% (0.03)
- **변경 방법**: [engine.py:539](../../../backend/backtest/engine.py#L539)에서 수정
```python
risk_free_rate_daily = 0.03 / 252  # 연 3%
```

### 2. 트레이너 비율 베타
- **현재 설정**: 베타 = 1.0 (시장과 동일)
- **한계**: 실제 시장(KOSPI) 대비 변동성을 반영하지 못함
- **향후 개선**: KOSPI 지수 데이터 추가 필요

### 3. 데이터 부족 시
- 일별 수익률 데이터가 2일 미만인 경우 계산 불가
- 결과: `sharpe_ratio`, `sortino_ratio`, `treynor_ratio` = `None` (NULL)
- UI 표시: "N/A"

---

## 🔄 향후 개선 사항

### 1. 실제 베타 계산
```python
# TODO: KOSPI 지수 데이터 추가
market_returns = get_kospi_returns(start_date, end_date)
beta = calculate_beta(daily_returns, market_returns)
treynor_ratio = (excess_return * 252) / beta
```

### 2. 무위험 이자율 동적 조회
```python
# TODO: 한국은행 API 연동
risk_free_rate = get_risk_free_rate(date_range)
```

### 3. 기타 지표 추가
- **칼마 비율** (Calmar Ratio): 수익률 / 최대 낙폭
- **정보 비율** (Information Ratio): 벤치마크 대비 초과 수익
- **오메가 비율** (Omega Ratio): 이익 확률 / 손실 확률

---

## 📚 참고 자료

### 논문 및 서적
- Sharpe, W.F. (1966). "Mutual Fund Performance"
- Sortino, F.A. (1994). "Downside Risk"
- Treynor, J.L. (1965). "How to Rate Management of Investment Funds"

### 온라인 자료
- [Investopedia - Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Investopedia - Sortino Ratio](https://www.investopedia.com/terms/s/sortinoratio.asp)
- [Investopedia - Treynor Ratio](https://www.investopedia.com/terms/t/treynorratio.asp)

---

**작성자**: Auto Trading System
**최종 수정**: 2025-10-08
