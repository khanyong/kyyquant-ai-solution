# 전략 및 지표 컬럼명 일관성 검증 리포트

생성일: 2025-09-29T14:30:20.530705+00:00

## 1. Supabase Indicators - Formula가 생성하는 컬럼명

| 지표명 | 타입 | 생성 패턴 | 예시 | output_columns |
|--------|------|-----------|------|----------------|
| `adx` | 📌 static | `adx` | `adx` | `adx` |
| `atr` | 📌 static | `atr` | `atr` | `atr` |
| `bollinger` | 📌 static | `bollinger_upper, bollinger_middle, bollinger_lower` | `bollinger_upper, bollinger_middle, bollinger_lower` | `bollinger_upper`, `bollinger_middle`, `bollinger_lower` |
| `cci` | 📌 static | `cci` | `cci` | `cci` |
| `close` | 📌 static | `close` | `close` | `close` |
| `dmi` | 📌 static | `dmi_plus_di, dmi_minus_di` | `dmi_plus_di, dmi_minus_di` | `dmi_plus_di`, `dmi_minus_di` |
| `ema` | 🔄 dynamic | `ema_{period}` | `ema_20` | `ema` |
| `ichimoku` | 📌 static | `ichimoku_tenkan, ichimoku_kijun, ichimoku_senkou_a, ichimoku_senkou_b, ichimoku_chikou` | `ichimoku_tenkan, ichimoku_kijun, ichimoku_senkou_a, ichimoku_senkou_b, ichimoku_chikou` | `ichimoku_tenkan`, `ichimoku_kijun`, `ichimoku_senkou_a`, `ichimoku_senkou_b`, `ichimoku_chikou` |
| `ma` | 📌 static | `ma` | `ma` | `ma` |
| `macd` | 📌 static | `macd_line, macd_signal, macd_hist` | `macd_line, macd_signal, macd_hist` | `macd_line`, `macd_signal`, `macd_hist` |
| `obv` | 📌 static | `obv` | `obv` | `obv` |
| `parabolic` | 📌 static | `psar, psar_trend` | `psar, psar_trend` | `psar`, `psar_trend` |
| `price` | 📌 static | `price` | `price` | `price` |
| `rsi` | 📌 static | `rsi` | `rsi` | `rsi` |
| `sma` | 🔄 dynamic | `sma_{period}` | `sma_20` | `sma` |
| `stochastic` | 📌 static | `stochastic_k, stochastic_d` | `stochastic_k, stochastic_d` | `stochastic_k`, `stochastic_d` |
| `volume` | 📌 static | `volume` | `volume` | `volume` |
| `volume_ma` | 🔄 dynamic | `volume_ma_{period}` | `volume_ma_20` | `volume_ma` |
| `vwap` | 📌 static | `vwap` | `vwap` | `vwap` |
| `williams` | 📌 static | `williams_r` | `williams_r` | `williams_r` |

**범례:**
- 🔄 dynamic: period 파라미터에 따라 컬럼명 변경 (예: sma_20, sma_60)
- 📌 static: 고정된 컬럼명 사용

## 2. 템플릿 전략 - 사용하는 지표 및 컬럼

### [템플릿] MACD 시그널

**사용 지표:**
- `macd` (fast=12, slow=26, signal=9)

**매수 조건에서 사용하는 컬럼:**
- `macd_line`
- `macd_signal`

**매도 조건에서 사용하는 컬럼:**
- `macd_line`
- `macd_signal`

### [템플릿] RSI 반전

**사용 지표:**
- `rsi` (period=14)

**매수 조건에서 사용하는 컬럼:**
- `rsi`

**매도 조건에서 사용하는 컬럼:**
- `rsi`

### [템플릿] 골든크로스

**사용 지표:**
- `sma` (period=20)
- `sma` (period=60)

**매수 조건에서 사용하는 컬럼:**
- `sma_20`
- `sma_60`

**매도 조건에서 사용하는 컬럼:**
- `sma_20`
- `sma_60`

### [템플릿] 복합 전략 A

**사용 지표:**
- `rsi` (period=14)
- `macd` (fast=12, slow=26, signal=9)
- `volume_ma` (period=20)

**매수 조건에서 사용하는 컬럼:**
- `macd_line`
- `macd_signal`
- `rsi`
- `volume`
- `volume_ma_20`

**매도 조건에서 사용하는 컬럼:**
- `macd_line`
- `macd_signal`
- `rsi`

### [템플릿] 복합 전략 B

**사용 지표:**
- `sma` (period=20)
- `bollinger` (std=2, period=20)
- `rsi` (period=14)

**매수 조건에서 사용하는 컬럼:**
- `bollinger_lower`
- `close`
- `rsi`
- `sma_20`

**매도 조건에서 사용하는 컬럼:**
- `bollinger_upper`
- `close`
- `rsi`

### [템플릿] 볼린저밴드

**사용 지표:**
- `bollinger` (std=2, period=20)
- `rsi` (period=14)

**매수 조건에서 사용하는 컬럼:**
- `bollinger_lower`
- `close`
- `rsi`

**매도 조건에서 사용하는 컬럼:**
- `bollinger_upper`
- `close`

### [템플릿] 스윙 트레이딩

**사용 지표:**
- `sma` (period=20)
- `sma` (period=60)
- `rsi` (period=14)
- `macd` (fast=12, slow=26, signal=9)

**매수 조건에서 사용하는 컬럼:**
- `macd_line`
- `rsi`
- `sma_20`
- `sma_60`

**매도 조건에서 사용하는 컬럼:**
- `rsi`
- `sma_20`
- `sma_60`

### [템플릿] 스캘핑

**사용 지표:**
- `sma` (period=5)
- `rsi` (period=14)

**매수 조건에서 사용하는 컬럼:**
- `close`
- `rsi`
- `sma_5`

**매도 조건에서 사용하는 컬럼:**
- `rsi`

## 3. 전략빌더(StrategyBuilder.tsx) - 사용 가능한 지표

| 지표 ID | 지표명 | 타입 | 기본 파라미터 |
|---------|--------|------|---------------|
| `ma` | MA (이동평균) | trend | period=20 |
| `sma` | SMA (단순이동평균) | trend | period=20 |
| `ema` | EMA (지수이동평균) | trend | period=20 |
| `bollinger` | 볼린저밴드 | volatility | period=20, std=2 |
| `rsi` | RSI | momentum | period=14 |
| `macd` | MACD | momentum | fast=12, slow=26, signal=9 |
| `stochastic` | 스토캐스틱 | momentum | k=14, d=3 |
| `ichimoku` | 일목균형표 | trend | tenkan=9, kijun=26, senkou=52, chikou=26 |
| `volume` | 거래량 | volume | period=20 |
| `obv` | OBV (누적거래량) | volume | (없음) |
| `vwap` | VWAP (거래량가중평균) | volume | (없음) |
| `atr` | ATR (변동성) | volatility | period=14 |
| `cci` | CCI | momentum | period=20 |
| `williams` | Williams %R | momentum | period=14 |
| `adx` | ADX (추세강도) | trend | period=14 |
| `dmi` | DMI (+DI/-DI) | trend | period=14 |
| `parabolic` | Parabolic SAR | trend | acc=0.02, max=0.2 |

## 4. 비교 분석 및 검증 결과

### 4.1 전략빌더 ↔ Supabase Indicators 일치 여부

| 전략빌더 지표 | Supabase 존재 | 비고 |
|--------------|--------------|------|
| `ma` | ✅ |  |
| `sma` | ✅ |  |
| `ema` | ✅ |  |
| `bollinger` | ✅ |  |
| `rsi` | ✅ |  |
| `macd` | ✅ |  |
| `stochastic` | ✅ |  |
| `ichimoku` | ✅ |  |
| `volume` | ✅ |  |
| `obv` | ✅ |  |
| `vwap` | ✅ |  |
| `atr` | ✅ |  |
| `cci` | ✅ |  |
| `williams` | ✅ |  |
| `adx` | ✅ |  |
| `dmi` | ✅ |  |
| `parabolic` | ✅ |  |

### 4.2 템플릿 전략 검증 결과

| 템플릿 전략 | 상태 | 비고 |
|------------|------|------|
| [템플릿] MACD 시그널 | ✅ | 정상 |
| [템플릿] RSI 반전 | ✅ | 정상 |
| [템플릿] 골든크로스 | ✅ | 정상 |
| [템플릿] 복합 전략 A | ✅ | 정상 |
| [템플릿] 복합 전략 B | ✅ | 정상 |
| [템플릿] 볼린저밴드 | ✅ | 정상 |
| [템플릿] 스윙 트레이딩 | ✅ | 정상 |
| [템플릿] 스캘핑 | ✅ | 정상 |

## 5. 결론

### 동적 컬럼명 생성 지표

- **`sma`**: `sma_{period}` 형태로 생성 (예: `sma_20`, `sma_60`)
- **`ema`**: `ema_{period}` 형태로 생성 (예: `ema_20`, `ema_50`)
- **`volume_ma`**: `volume_ma_{period}` 형태로 생성 (예: `volume_ma_20`)

**업데이트 (2025-10-04):**
- preflight.py의 regex 패턴 수정: f-string 내부 중괄호 정확히 파싱
- calculator.py의 캐시 키 수정: params를 포함하여 동일 지표의 다른 period 구분

### 정적 컬럼명 생성 지표

총 17개의 지표가 고정된 컬럼명을 사용합니다.

### 검증 요약

- **전체 지표 수**: 20개
- **전체 템플릿 수**: 8개
- **전략빌더 지표 수**: 17개
