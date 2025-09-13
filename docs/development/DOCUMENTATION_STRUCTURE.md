# 📚 프로젝트 문서 구조 정리

## 🎯 최종 유효 문서 (루트 폴더 유지)

### 1. 핵심 문서
- `README.md` - 프로젝트 메인 설명서
- `SYSTEM_STATUS_DIAGNOSIS.md` - 현재 시스템 상태 진단 (최신)
- `KIWOOM_REST_API_INTEGRATION.md` - 키움 REST API 통합 계획 (최종)

### 2. 사용자 가이드
- `BACKTEST_GUIDE.md` - 백테스트 시스템 사용 가이드
- `INVESTMENT_DATA_COLLECTION_GUIDE.md` - 투자 데이터 수집 가이드
- `STRATEGY_WORKFLOW.md` - 전략 워크플로우 가이드

### 3. 개발 로드맵
- `DEVELOPMENT_ROADMAP.md` - 전체 개발 로드맵

---

## 📦 보관용 문서 (docs/archive 폴더로 이동)

### 초기 계획 문서 (구버전)
- `KIWOOM_API_INTEGRATION_PLAN.md` - Windows 기반 초기 계획
- `KIWOOM_API_SETUP.md` - OpenAPI+ 설정 가이드
- `KIWOOM_IMPLEMENTATION_ROADMAP.md` - 초기 구현 로드맵
- `COMPREHENSIVE_DEVELOPMENT_ROADMAP.md` - 초기 종합 로드맵

### 대안 검토 문서
- `SYNOLOGY_N8N_KIWOOM_IMPLEMENTATION.md` - 키움 REST API 미지원 가정 문서
- `MULTI_USER_ARCHITECTURE.md` - 다중 사용자 초기 설계
- `CLOUD_NATIVE_TRADING_ARCHITECTURE.md` - 클라우드 네이티브 초기 설계

### 비교/분석 문서
- `N8N_VS_DIRECT_API_COMPARISON.md` - N8N vs 직접 API 비교
- `SUPABASE_STRUCTURE_ANALYSIS.md` - Supabase 구조 분석

---

## 🗂️ 계획 문서 (docs/planning 폴더로 이동)

### 시스템 개선 계획
- `CURRENT_SYSTEM_ENHANCEMENT_PLAN.md` - 현재 시스템 개선 계획
- `NAS_MIGRATION_ROADMAP.md` - NAS 마이그레이션 로드맵
- `SUPABASE_VERCEL_NAS_ARCHITECTURE.md` - 통합 아키텍처 계획

### N8N 관련
- `N8N_REALTIME_TRADING_SYSTEM.md` - N8N 실시간 거래 시스템
- `SYNOLOGY_N8N_IMPLEMENTATION.md` - 시놀로지 N8N 구현 계획

---

## 🗑️ 삭제 대상 문서

### 중복/테스트 문서
- `strategy_evaluation_complex_b.md` - 전략 평가 임시 문서
- `strategy_evaluation_report.md` - 전략 평가 임시 문서
- `strategy_evaluation_report_professional.md` - 전략 평가 임시 문서

---

## 📂 최종 폴더 구조

```
auto_stock/
├── 📄 README.md                              # 메인 문서
├── 📄 SYSTEM_STATUS_DIAGNOSIS.md             # 현재 상태
├── 📄 KIWOOM_REST_API_INTEGRATION.md         # 최종 통합 계획
├── 📄 BACKTEST_GUIDE.md                      # 백테스트 가이드
├── 📄 INVESTMENT_DATA_COLLECTION_GUIDE.md    # 데이터 수집 가이드
├── 📄 STRATEGY_WORKFLOW.md                   # 전략 워크플로우
├── 📄 DEVELOPMENT_ROADMAP.md                 # 개발 로드맵
├── 📄 DOCUMENTATION_STRUCTURE.md             # 문서 구조 설명 (이 파일)
│
├── docs/
│   ├── archive/                              # 보관용 (참고용)
│   │   ├── KIWOOM_API_INTEGRATION_PLAN.md
│   │   ├── KIWOOM_API_SETUP.md
│   │   ├── KIWOOM_IMPLEMENTATION_ROADMAP.md
│   │   ├── COMPREHENSIVE_DEVELOPMENT_ROADMAP.md
│   │   ├── SYNOLOGY_N8N_KIWOOM_IMPLEMENTATION.md
│   │   ├── MULTI_USER_ARCHITECTURE.md
│   │   ├── CLOUD_NATIVE_TRADING_ARCHITECTURE.md
│   │   ├── N8N_VS_DIRECT_API_COMPARISON.md
│   │   └── SUPABASE_STRUCTURE_ANALYSIS.md
│   │
│   └── planning/                             # 계획 문서
│       ├── CURRENT_SYSTEM_ENHANCEMENT_PLAN.md
│       ├── NAS_MIGRATION_ROADMAP.md
│       ├── SUPABASE_VERCEL_NAS_ARCHITECTURE.md
│       ├── N8N_REALTIME_TRADING_SYSTEM.md
│       └── SYNOLOGY_N8N_IMPLEMENTATION.md
│
├── src/                                      # 소스 코드
├── backend/                                  # 백엔드
└── trading-server/                           # 실전 매매 서버 (예정)
```

---

## 🔄 문서 정리 명령어

```bash
# 1. 보관용 문서 이동
mv KIWOOM_API_INTEGRATION_PLAN.md docs/archive/
mv KIWOOM_API_SETUP.md docs/archive/
mv KIWOOM_IMPLEMENTATION_ROADMAP.md docs/archive/
mv COMPREHENSIVE_DEVELOPMENT_ROADMAP.md docs/archive/
mv SYNOLOGY_N8N_KIWOOM_IMPLEMENTATION.md docs/archive/
mv MULTI_USER_ARCHITECTURE.md docs/archive/
mv CLOUD_NATIVE_TRADING_ARCHITECTURE.md docs/archive/
mv N8N_VS_DIRECT_API_COMPARISON.md docs/archive/
mv SUPABASE_STRUCTURE_ANALYSIS.md docs/archive/

# 2. 계획 문서 이동
mv CURRENT_SYSTEM_ENHANCEMENT_PLAN.md docs/planning/
mv NAS_MIGRATION_ROADMAP.md docs/planning/
mv SUPABASE_VERCEL_NAS_ARCHITECTURE.md docs/planning/
mv N8N_REALTIME_TRADING_SYSTEM.md docs/planning/
mv SYNOLOGY_N8N_IMPLEMENTATION.md docs/planning/

# 3. 임시 문서 삭제
rm strategy_evaluation_complex_b.md
rm strategy_evaluation_report.md
rm strategy_evaluation_report_professional.md
```

---

## ✅ 정리 후 효과

1. **명확한 구조**: 현재 유효한 문서와 보관용 문서 구분
2. **혼란 제거**: 상충되는 정보를 담은 문서들 분리
3. **빠른 접근**: 핵심 문서만 루트에 유지
4. **이력 보존**: 과거 계획 문서들은 archive에 보관

## 📝 주의사항

- **KIWOOM_REST_API_INTEGRATION.md**가 최종 통합 계획입니다
- 키움증권 REST API는 실제로 제공되며 (`https://api.kiwoom.com`)
- Windows 서버 없이 구현 가능합니다