# 🚀 Auto Stock Trading System - 프로젝트 개요

## 📌 프로젝트 현황

### ✅ 운영 중
- **백테스트 시스템**: React + TypeScript + Supabase
- **배포**: Vercel (Frontend) + Supabase (Backend)
- **기능**: 전략 빌더, 필터링, 백테스트, 결과 시각화

### 🔄 개발 예정
- **실전 매매**: 키움증권 REST API 연동
- **자동화**: N8N + 시놀로지 NAS
- **다중 사용자**: OAuth 2.0 기반

## 📂 문서 구조

### 핵심 문서 (루트)
```
📄 README.md                    - 프로젝트 소개
📄 SYSTEM_STATUS_DIAGNOSIS.md   - 현재 상태 진단
📄 KIWOOM_REST_API_INTEGRATION.md - 키움 API 통합 (최종)
📄 BACKTEST_GUIDE.md            - 백테스트 가이드
📄 DEVELOPMENT_ROADMAP.md       - 개발 로드맵
```

### 보관 문서
```
docs/archive/  - 구버전/대안 문서
docs/planning/ - 계획 문서
```

## 🏗️ 시스템 아키텍처

### 현재 (백테스트)
```
Vercel (React) ← → Supabase (DB/Auth)
```

### 목표 (실전 매매)
```
Vercel → Supabase → NAS(N8N) → 키움 REST API
                              ↓
                    OAuth 2.0 인증
                    https://api.kiwoom.com
```

## 🔑 핵심 기술

- **Frontend**: React, TypeScript, MUI
- **Backend**: Supabase, FastAPI
- **자동화**: N8N, Docker
- **API**: 키움증권 REST API (OAuth 2.0)

## 📋 즉시 실행 가능한 작업

1. 키움 REST API 앱 등록
2. OAuth 2.0 인증 구현
3. N8N 워크플로우 설정
4. 모의투자 테스트

## 📞 문의

- GitHub Issues: [프로젝트 이슈](https://github.com/yourusername/auto_stock/issues)
- 문서: `DOCUMENTATION_STRUCTURE.md` 참조