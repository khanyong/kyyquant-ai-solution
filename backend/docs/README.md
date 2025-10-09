# Auto Stock Backend Documentation

백엔드 시스템 관련 모든 문서를 체계적으로 관리합니다.

---

## 📁 문서 구조

```
docs/
├── deployment/          # 배포 및 인프라 관련 문서
├── strategy/           # 전략 구현 및 샘플 문서
├── analysis/           # 분석 및 디버깅 리포트
└── guides/             # 개발 가이드 및 튜토리얼
```

---

## 🚀 Deployment (배포)

배포, 환경 설정, 인프라 관련 문서

| 문서 | 설명 |
|------|------|
| [NAS_DEPLOYMENT.md](deployment/NAS_DEPLOYMENT.md) | NAS 서버 배포 가이드 |
| [NAS_INFO.md](deployment/NAS_INFO.md) | NAS 서버 정보 및 접속 방법 |
| [SYNOLOGY_SETUP.md](deployment/SYNOLOGY_SETUP.md) | Synology NAS 초기 설정 |
| [KIWOOM_INFO.md](deployment/KIWOOM_INFO.md) | 키움 API 연동 정보 |
| [FRONTEND_ENV.md](deployment/FRONTEND_ENV.md) | 프론트엔드 환경 변수 설정 |

---

## 📊 Strategy (전략)

트레이딩 전략 구현, 샘플, 설정 문서

| 문서 | 설명 |
|------|------|
| [STAGED_BUY_SELL_IMPLEMENTATION.md](strategy/STAGED_BUY_SELL_IMPLEMENTATION.md) | 단계별 매수/매도 구현 가이드 |
| [STAGE_BASED_TRADING_ANALYSIS.md](strategy/STAGE_BASED_TRADING_ANALYSIS.md) | 단계별 거래 분석 |
| [UI_STRATEGY_IMPLEMENTATION.md](strategy/UI_STRATEGY_IMPLEMENTATION.md) | UI 전략 설정 구현 가이드 |
| [STRATEGY_SAMPLES.md](strategy/STRATEGY_SAMPLES.md) | 기본 전략 샘플 모음 |
| [STRATEGY_SAMPLES_WITH_STAGED_BUY.md](strategy/STRATEGY_SAMPLES_WITH_STAGED_BUY.md) | 단계별 매수 전략 샘플 |
| [SUPABASE_STRATEGY_SAMPLES.md](strategy/SUPABASE_STRATEGY_SAMPLES.md) | Supabase 전략 데이터 샘플 |

---

## 🔍 Analysis (분석)

백테스트 분석, 버그 리포트, 검증 문서

| 문서 | 설명 |
|------|------|
| [STRATEGY_A1_VALIDATION_REPORT.md](analysis/STRATEGY_A1_VALIDATION_REPORT.md) | ⭐ 전략 A1 검증 리포트 (최신) |
| [BACKTEST_CONDITION_ANALYSIS.md](analysis/BACKTEST_CONDITION_ANALYSIS.md) | 백테스트 조건 분석 |
| [COMBINE_WITH_FIX_SUMMARY.md](analysis/COMBINE_WITH_FIX_SUMMARY.md) | combineWith 조건 수정 요약 |
| [INDICATOR_COLUMN_COMPARISON.md](analysis/INDICATOR_COLUMN_COMPARISON.md) | 지표 컬럼명 비교 분석 |
| [TRADE_REASON_DEBUG.md](analysis/TRADE_REASON_DEBUG.md) | 거래 이유 디버깅 리포트 |
| [sql_comparison.md](analysis/sql_comparison.md) | SQL 쿼리 비교 분석 |

---

## 📖 Guides (가이드)

개발 가이드, 문제 해결 방법

| 문서 | 설명 |
|------|------|
| [INDICATOR_NAMING_FIX_GUIDE.md](guides/INDICATOR_NAMING_FIX_GUIDE.md) | 지표 네이밍 수정 가이드 |

---

## 🔥 최근 업데이트

### 2025-10-08
- ⭐ **[전략 A1 검증 리포트](analysis/STRATEGY_A1_VALIDATION_REPORT.md)** 생성
  - Stop Loss 로직 불일치 원인 분석
  - Dynamic Stop Loss 강제 활성화 문제 발견
  - 수정 방안 및 테스트 계획 제시

---

## 📌 빠른 참조

### 문제 해결

- **백테스트 결과가 이상해요**: [STRATEGY_A1_VALIDATION_REPORT.md](analysis/STRATEGY_A1_VALIDATION_REPORT.md)
- **단계별 매수/매도가 작동 안 해요**: [STAGED_BUY_SELL_IMPLEMENTATION.md](strategy/STAGED_BUY_SELL_IMPLEMENTATION.md)
- **지표 이름이 안 맞아요**: [INDICATOR_NAMING_FIX_GUIDE.md](guides/INDICATOR_NAMING_FIX_GUIDE.md)

### 개발

- **새 전략 만들기**: [STRATEGY_SAMPLES.md](strategy/STRATEGY_SAMPLES.md)
- **UI에서 전략 설정**: [UI_STRATEGY_IMPLEMENTATION.md](strategy/UI_STRATEGY_IMPLEMENTATION.md)

### 배포

- **NAS 서버 배포**: [NAS_DEPLOYMENT.md](deployment/NAS_DEPLOYMENT.md)
- **환경 변수 설정**: [FRONTEND_ENV.md](deployment/FRONTEND_ENV.md)

---

## 📝 문서 작성 가이드

새 문서를 추가할 때는 적절한 카테고리에 배치하세요:

- `deployment/` - 서버, 인프라, 환경 설정
- `strategy/` - 전략 로직, 샘플, 구현
- `analysis/` - 버그 분석, 검증, 리포트
- `guides/` - 튜토리얼, 가이드, 문제 해결

---

**마지막 업데이트**: 2025-10-08
