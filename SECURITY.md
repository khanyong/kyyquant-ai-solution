# 🔒 보안 가이드

## ⚠️ 긴급: API 키 재생성 필요

이 저장소에서 `.env` 파일이 Git 추적에서 제거되었습니다. 하지만 과거에 노출된 키들은 **즉시 재생성**해야 합니다.

### 즉시 재생성해야 할 키들

1. **Supabase Keys** (최우선)
   - Supabase Dashboard → Settings → API
   - `ANON_KEY` 재생성
   - `SERVICE_ROLE_KEY` 재생성

2. **GitHub Personal Access Token**
   - GitHub → Settings → Developer settings → Personal access tokens
   - 기존 토큰 삭제 후 새로 생성

3. **Kiwoom API Keys**
   - 키움증권 OpenAPI 포털에서 재발급

4. **N8N API Key**
   - N8N → Settings → API Keys
   - 기존 키 삭제 후 새로 생성

## 환경 변수 설정 가이드

### 1. 개발 환경 설정

```bash
# 1. .env.example을 복사하여 .env 생성
cp .env.example .env

# 2. .env 파일 편집
# - 실제 API 키 값으로 변경
# - 절대 Git에 커밋하지 마세요!
```

### 2. 환경 변수 분리 원칙

#### Frontend (.env)
```bash
# ✅ 공개 가능 (RLS로 보호됨)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...

# ❌ 절대 포함하지 마세요
# SUPABASE_SERVICE_ROLE_KEY - 백엔드 전용!
```

#### Backend (.env)
```bash
# ✅ Service Role만 사용
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# ❌ 사용 금지
# SUPABASE_ANON_KEY - 프론트엔드 전용!
```

### 3. Git 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가?
- [ ] `git status`에서 `.env` 파일이 보이지 않는가?
- [ ] `.env.example`에는 실제 키가 없는가?
- [ ] 커밋 전 `git diff`로 민감 정보 확인했는가?

### 4. 배포 환경 설정

#### Vercel
1. Project Settings → Environment Variables
2. 각 변수를 개별적으로 추가
3. Production/Preview/Development 환경별 설정

#### Netlify
1. Site settings → Build & deploy → Environment
2. 환경 변수 추가

#### 백엔드 서버 (NAS/VPS)
```bash
# 서버에 직접 .env 파일 생성 (Git 사용 안 함)
nano /path/to/backend/.env

# 또는 systemd 환경 변수 사용
[Service]
Environment="SUPABASE_SERVICE_ROLE_KEY=..."
```

## Supabase RLS (Row Level Security) 설정

### 필수 보안 정책

모든 테이블에 다음 RLS 정책을 적용하세요:

```sql
-- 1. RLS 활성화
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- 2. SELECT 정책: 본인 데이터만 조회
CREATE POLICY "Users can view own data"
ON your_table
FOR SELECT
USING (auth.uid() = user_id);

-- 3. INSERT 정책: 본인 계정으로만 생성
CREATE POLICY "Users can insert own data"
ON your_table
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- 4. UPDATE 정책: 본인 데이터만 수정
CREATE POLICY "Users can update own data"
ON your_table
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 5. DELETE 정책: 본인 데이터만 삭제
CREATE POLICY "Users can delete own data"
ON your_table
FOR DELETE
USING (auth.uid() = user_id);
```

## 백엔드 보안 강화

### Service Role 사용 예시

```python
# ❌ 잘못된 방법
from supabase import create_client
supabase = create_client(
    supabase_url,
    supabase_anon_key  # 백엔드에서 ANON_KEY 사용 금지!
)

# ✅ 올바른 방법
supabase = create_client(
    supabase_url,
    supabase_service_role_key  # Service Role 사용
)

# 사용자 인증 검증
def verify_user_token(token: str):
    try:
        # JWT 토큰 검증
        user = supabase.auth.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")
```

### API 엔드포인트 보안

```python
from fastapi import Header, HTTPException

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = authorization.replace("Bearer ", "")
    user = verify_user_token(token)
    return user

@app.get("/api/protected")
async def protected_route(user = Depends(get_current_user)):
    # 사용자별 데이터만 반환
    data = supabase.table("data").select("*").eq("user_id", user.id).execute()
    return data
```

## 보안 모니터링

### 정기 점검 항목

- [ ] **주간**: Supabase Auth Logs 확인
- [ ] **주간**: API 사용량 모니터링 (비정상 트래픽 탐지)
- [ ] **월간**: API 키 로테이션
- [ ] **월간**: RLS 정책 검토
- [ ] **분기**: 전체 보안 감사

### 의심스러운 활동 감지 시

1. **즉시**: 모든 API 키 재생성
2. **즉시**: Supabase Auth에서 모든 세션 무효화
3. Git 히스토리 점검
4. 로그 분석

## 문의

보안 문제 발견 시: security@kyyquant.com
