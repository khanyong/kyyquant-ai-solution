# Supabase 프로젝트 설정 가이드

## 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 접속 후 로그인
2. "New project" 클릭
3. 프로젝트 정보 입력:
   - Project name: `kyyquant-ai`
   - Database Password: 강력한 비밀번호 설정
   - Region: `Northeast Asia (Seoul)` 선택 (가장 가까운 지역)
4. "Create new project" 클릭

## 2. 프로젝트 API 키 확인

프로젝트 생성 완료 후:

1. 좌측 메뉴에서 "Settings" → "API" 클릭
2. 다음 정보 복사:
   - `Project URL`: https://[your-project-ref].supabase.co
   - `anon/public key`: 공개 키
   - `service_role key`: 서버 사이드용 키 (보안 주의!)

## 3. 환경 변수 설정

`.env.local` 파일을 생성하고 복사한 정보 입력:

```env
VITE_SUPABASE_URL=https://[your-project-ref].supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

## 4. 데이터베이스 스키마 적용

### 방법 1: SQL Editor 사용 (추천)

1. Supabase 대시보드에서 "SQL Editor" 클릭
2. "New query" 클릭
3. `supabase/schema.sql` 파일의 내용을 복사하여 붙여넣기
4. "Run" 버튼 클릭하여 실행

### 방법 2: Supabase CLI 사용

```bash
# Supabase CLI 설치
npm install -g supabase

# 로그인
supabase login

# 프로젝트 연결
supabase link --project-ref [your-project-ref]

# 스키마 적용
supabase db push
```

## 5. Authentication 설정

1. Supabase 대시보드에서 "Authentication" → "Providers" 클릭
2. Email 인증 활성화:
   - Email 토글 ON
   - Confirm email 설정 (선택사항)
3. 추가 인증 제공자 설정 (선택사항):
   - Google OAuth
   - GitHub OAuth
   - Kakao OAuth

## 6. Row Level Security (RLS) 확인

1. "Database" → "Tables" 클릭
2. 각 테이블의 RLS가 활성화되어 있는지 확인
3. 스키마에 정의된 정책이 적용되었는지 확인

## 7. Realtime 설정

1. "Database" → "Replication" 클릭
2. 실시간 업데이트가 필요한 테이블 활성화:
   - `realtime_prices`
   - `orders`
   - `trading_signals`
   - `portfolio`

## 8. Storage 설정 (선택사항)

차트 이미지나 리포트 파일 저장이 필요한 경우:

1. "Storage" → "Create bucket" 클릭
2. Bucket 생성:
   - Name: `charts`
   - Public: OFF (보안)
3. 정책 설정

## 9. Edge Functions 설정 (선택사항)

복잡한 비즈니스 로직이 필요한 경우:

```bash
# Edge Functions 생성
supabase functions new calculate-portfolio

# 배포
supabase functions deploy calculate-portfolio
```

## 10. 테스트

프로젝트에서 다음 명령 실행:

```bash
npm run dev
```

브라우저 콘솔에서 연결 확인:

```javascript
// 개발자 도구 콘솔에서 테스트
const { data, error } = await window.supabase.from('stocks').select('*').limit(1)
console.log(data, error)
```

## 주요 테이블 설명

### 키움 API 연동 테이블

- **stocks**: 종목 마스터 정보
- **price_data**: 일별 가격 데이터 (OHLCV)
- **realtime_prices**: 실시간 호가/체결 정보
- **orders**: 주문 내역
- **portfolio**: 보유 종목
- **account_balance**: 계좌 잔고

### 전략 관련 테이블

- **strategies**: 매매 전략 설정
- **backtest_results**: 백테스트 결과
- **trading_signals**: 매매 신호

### 기타 테이블

- **market_index**: 시장 지수 (KOSPI, KOSDAQ)
- **news_alerts**: 뉴스 및 공시 정보

## 보안 체크리스트

- [ ] RLS 정책이 모든 테이블에 적용됨
- [ ] Service Role Key는 서버 사이드에서만 사용
- [ ] 환경 변수 파일(.env.local)이 .gitignore에 포함됨
- [ ] API 요청 rate limiting 설정
- [ ] 백업 정책 설정

## 문제 해결

### 연결 오류
- API 키와 URL이 정확한지 확인
- CORS 설정 확인 (Supabase 대시보드 → Settings → API)

### 권한 오류
- RLS 정책 확인
- 사용자 인증 상태 확인

### 성능 이슈
- 인덱스 생성 확인
- 쿼리 최적화
- Connection pooling 설정

## 유용한 링크

- [Supabase 문서](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Supabase Dashboard](https://app.supabase.com)