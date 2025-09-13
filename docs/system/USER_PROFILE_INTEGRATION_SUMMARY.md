# 사용자 프로필 통합 시스템 구현 완료

## 개요
기존 `profiles` 테이블과 새로운 확장 테이블들을 통합하여 완전한 사용자 관리 시스템을 구현했습니다.

## 데이터베이스 구조

### 1. 테이블 관계도
```
auth.users (Supabase Auth)
    ↓
profiles (기본 프로필)
    ├── user_profiles_extended (확장 프로필)
    ├── user_api_keys (암호화된 API 키)
    └── user_trading_accounts_secure (거래 계좌)
```

### 2. 주요 테이블

#### profiles (기존)
- `id` (UUID) - auth.users.id와 연결
- `email` - 사용자 이메일
- `name` - 사용자 이름
- `kiwoom_account` - 레거시 키움 계좌 번호

#### user_profiles_extended (신규)
- `user_id` (UUID) - profiles.id와 연결
- `display_name` - 표시 이름
- `phone_number` - 전화번호
- `birth_date` - 생년월일
- `investor_type` - 투자자 유형
- `risk_tolerance` - 위험 감수도
- `preferred_market` - 선호 시장
- 알림 설정 필드들

#### user_api_keys (신규)
- Vault 암호화를 사용한 안전한 API 키 저장
- 제공자별 (kiwoom, ebest, kis 등) 키 관리
- 테스트/실전 모드 구분

#### user_trading_accounts_secure (신규)
- 거래 계좌 정보
- OAuth 토큰 암호화 저장
- 계좌 잔고 및 상태 관리

## 통합 뷰

### user_complete_profile
전체 사용자 정보를 한 번에 조회할 수 있는 통합 뷰:
- 기본 프로필 정보
- 확장 프로필 정보
- 활성 API 키 수
- 연결된 거래 계좌 수
- 계정 상태

### user_api_status
사용자별 API 키 상태 모니터링 뷰

### user_trading_status
거래 계좌 상태 및 잔고 모니터링 뷰

## 마이그레이션

### migrate_existing_profiles()
기존 profiles 데이터를 새 테이블 구조로 마이그레이션하는 함수:
1. profiles → user_profiles_extended
2. kiwoom_account → user_trading_accounts_secure

## 구현된 기능

### 1. MyPage 컴포넌트
- **프로필 관리**: 개인정보 수정
- **API 키 관리**: Vault 암호화 저장/조회
- **계좌 연결**: OAuth 2.0 기반 증권사 연동
- **보안 설정**: 비밀번호 변경, 2FA
- **알림 설정**: 이메일/SMS/푸시 알림

### 2. 인증 서비스 확장
```typescript
// 기본 프로필 조회
authService.getProfile(userId)

// 전체 프로필 조회 (확장 정보 포함)
authService.getFullProfile(userId)

// 확장 프로필 업데이트
authService.updateExtendedProfile(userId, updates)
```

### 3. 보안 기능
- pgsodium을 통한 Vault 암호화
- RLS 정책으로 데이터 접근 제어
- API 키 마스킹 표시
- 접근 로그 기록

## 사용 방법

### 1. Supabase 설정
```sql
-- 1. pgsodium 확장 활성화 (Supabase 대시보드에서)
-- 2. 스키마 파일 실행 순서:
-- - userApiKeysSchema.sql
-- - userProfilesIntegration.sql
```

### 2. 환경 변수 설정
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### 3. 사용자 플로우
1. 사용자 로그인
2. 헤더의 사람 아이콘 클릭 → MyPage 이동
3. API 키 입력 → Vault에 암호화 저장
4. 거래 계좌 연결 → OAuth 인증
5. 자동매매 설정 및 실행

## 다음 단계

1. **Supabase 배포**
   - userApiKeysSchema.sql 실행
   - userProfilesIntegration.sql 실행
   - pgsodium 확장 활성화

2. **OAuth 설정**
   - 키움증권 OAuth 앱 등록
   - 콜백 URL 설정
   - 환경 변수 추가

3. **테스트**
   - 신규 사용자 가입 플로우
   - 기존 사용자 마이그레이션
   - API 키 저장/조회
   - 거래 계좌 연결

## 파일 위치

- `/src/utils/userApiKeysSchema.sql` - API 키 및 확장 프로필 스키마
- `/src/utils/userProfilesIntegration.sql` - 통합 뷰 및 마이그레이션
- `/src/utils/tradingAccountSchema.sql` - 거래 계좌 스키마
- `/src/pages/MyPage.tsx` - 마이페이지 UI
- `/src/services/auth.ts` - 인증 서비스 확장
- `/src/services/kiwoomAuthSecure.ts` - 안전한 키움 인증

## 보안 고려사항

1. **암호화**
   - 모든 민감한 정보는 Vault로 암호화
   - 클라이언트에서는 마스킹된 값만 표시

2. **접근 제어**
   - RLS로 사용자별 데이터 격리
   - 관리자만 전체 데이터 접근 가능

3. **감사 로그**
   - API 키 사용 기록
   - 거래 계좌 접근 로그

## 문제 해결

### Q: profiles 테이블과 새 테이블의 관계는?
A: profiles는 기본 정보를 저장하고, 새 테이블들은 확장 정보를 저장합니다. auth.users.id를 통해 모두 연결됩니다.

### Q: 기존 사용자 데이터는 어떻게 되나요?
A: migrate_existing_profiles() 함수로 자동 마이그레이션됩니다.

### Q: API 키는 어떻게 보호되나요?
A: Supabase Vault (pgsodium)로 서버 측에서 암호화되어 저장됩니다.