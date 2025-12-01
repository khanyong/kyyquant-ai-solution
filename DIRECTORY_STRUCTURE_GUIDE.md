# 프로젝트 폴더 구조 및 파일 관리 규칙

이 문서는 프로젝트의 폴더 구조와 각 폴더에 저장되어야 할 파일들의 규칙을 정의합니다.

## 📂 루트 디렉토리 (Root)
**필수 설정 파일 및 프로젝트 진입점만 위치합니다.**
- `README.md`: 프로젝트 소개 및 시작 가이드
- `MASTER_ROADMAP.md`: 전체 프로젝트 로드맵
- `package.json`, `tsconfig.json`, `vite.config.ts`: 프로젝트 설정 파일
- `.env`: 환경 변수 파일
- `docker-compose.yml`: 도커 설정 파일

---

## 📂 docs/ (문서)
프로젝트 관련 모든 문서는 이곳으로 이동합니다.

| 하위 폴더 | 설명 | 예시 파일 |
| :--- | :--- | :--- |
| **`guides/`** | 사용 가이드, 매뉴얼, 규칙 | `AUTO_TRADING_GUIDE.md`, `CODE_REVIEW_RULES.md` |
| **`plans/`** | 개발 계획, 설계 문서 | `REFACTORING_PLAN.md`, `SYSTEM_ARCHITECTURE.md` |
| **`issues/`** | 버그 리포트, 문제 해결 기록 | `KIWOOM_API_500_ERROR.md`, `SYNC_ISSUE_FIX.md` |
| **`setup/`** | 설치 및 환경 설정 가이드 | `SETUP_CHECKLIST.md`, `KIWOOM_SETUP.md` |
| **`archive/`** | 완료되었거나 오래된 문서 | `INVESTOR_REPORT_2024.md`, `OLD_PLAN.md` |

---

## 📂 scripts/ (스크립트)
유틸리티, 유지보수, 테스트용 스크립트 (`.js`, `.py`, `.bat`, `.sh`)는 이곳으로 이동합니다.

| 하위 폴더 | 설명 | 예시 파일 |
| :--- | :--- | :--- |
| **`maintenance/`** | DB 점검, 상태 확인, 청소 | `check_db.js`, `check_server_status.bat` |
| **`sync/`** | 데이터 동기화 관련 스크립트 | `sync_balance.js`, `sync_portfolio.py` |
| **`test/`** | 기능 테스트 스크립트 | `test_backend_api.js`, `test_order.js` |
| **`utils/`** | 기타 보조 도구 | `read_env.js`, `add_uuids.js` |

---

## 📂 sql/ (데이터베이스)
SQL 쿼리 파일은 목적에 따라 분류하여 저장합니다.

| 하위 폴더 | 설명 | 예시 파일 |
| :--- | :--- | :--- |
| **`schema/`** | 테이블 생성, 초기 데이터 (Seed) | `create_tables.sql`, `seed_data.sql` |
| **`patches/`** | 버그 수정, 컬럼 변경, 로직 업데이트 | `fix_rls_policy.sql`, `update_columns.sql` |
| **`verification/`** | 데이터 검증 및 조회 쿼리 | `check_balance.sql`, `verify_data.sql` |

---

## 📂 소스 코드
- **`backend/`**: Python FastAPI 백엔드 소스 코드
- **`src/`**: React 프론트엔드 소스 코드
- **`supabase/`**: Supabase 관련 설정 및 마이그레이션 파일

## ⚠️ 파일 이동 시 주의사항
스크립트나 코드를 이동할 때는 반드시 **상대 경로(`../../.env` 등)**를 확인하고 수정해야 합니다.
