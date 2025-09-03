# 🔗 Railway, Vercel, Supabase 연결 구조

## 🎯 각 서비스의 역할

### 1. **Vercel** (프론트엔드)
- **역할**: React 웹사이트 호스팅
- **URL**: `https://your-site.vercel.app`
- **담당**: HTML, CSS, JavaScript (사용자가 보는 화면)

### 2. **Railway** (백엔드)
- **역할**: Python API 서버 실행
- **URL**: `https://your-api.railway.app`
- **담당**: 비즈니스 로직, 계산, API 처리

### 3. **Supabase** (데이터베이스)
- **역할**: 데이터 저장소
- **URL**: `https://xxxxx.supabase.co`
- **담당**: 전략, 사용자, 거래 데이터 저장

## 🔄 실제 연결 과정

### Step 1: Railway 배포
```bash
# 1. Railway.app 가입 (무료)
# 2. New Project 클릭
# 3. Deploy from GitHub repo 선택
# 4. backend 폴더 선택
# 5. 자동 배포 시작!
```

### Step 2: Railway 환경 변수 설정
```
Railway Dashboard > Variables 탭에서:

SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_KEY = eyJhbGc...
PORT = 8000
```

### Step 3: Vercel에서 Railway API 연결
```javascript
// frontend/.env.production
REACT_APP_API_URL=https://your-api.railway.app

// frontend/src/api/config.js
const API_URL = process.env.REACT_APP_API_URL;

// API 호출 예시
fetch(`${API_URL}/api/strategies`)
```

## 📊 전체 데이터 흐름

```
사용자가 "전략 생성" 버튼 클릭
         ↓
[1] Vercel (React)
    - 사용자 입력 받음
    - API 호출 준비
         ↓
[2] Railway (Python)
    - POST /api/strategy 요청 받음
    - 데이터 검증
    - 비즈니스 로직 실행
         ↓
[3] Supabase (PostgreSQL)
    - 전략 데이터 저장
    - 응답 반환
         ↓
[2] Railway → [1] Vercel
    - 성공 응답 전송
         ↓
사용자 화면에 "저장 완료" 표시
```

## 🔐 연결 설정 상세

### 1. Railway 설정 (Python 백엔드)
```python
# api_server.py
import os
from supabase import create_client

# Railway 환경변수에서 가져옴
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Supabase 연결
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# API 엔드포인트
@app.post("/api/strategy")
async def create_strategy(data):
    # Supabase에 저장
    result = supabase.table('strategies').insert(data).execute()
    return {"success": True}
```

### 2. Vercel 설정 (React 프론트엔드)
```javascript
// src/services/api.js
const API_URL = process.env.REACT_APP_API_URL;

export const createStrategy = async (strategyData) => {
  const response = await fetch(`${API_URL}/api/strategy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(strategyData)
  });
  return response.json();
};
```

### 3. Supabase 설정
```sql
-- Supabase Dashboard에서 실행
CREATE TABLE strategies (
  id UUID PRIMARY KEY,
  name TEXT,
  indicators JSONB,
  user_id UUID
);

-- API 키 생성
-- Settings > API > anon key 복사
```

## 🎯 실제 사용 시나리오

### 시나리오 1: 사용자가 전략 생성
```
1. 사용자 → Vercel 사이트 접속
2. 전략 설정 입력
3. "저장" 클릭
4. Vercel → Railway API 호출
5. Railway → Supabase 저장
6. 결과 → 사용자 화면
```

### 시나리오 2: 자동매매 실행 (9시)
```
1. Railway Python (24시간 실행 중)
2. 9시 되면 자동 실행
3. Supabase에서 활성 전략 조회
4. 한국투자 API 호출
5. 주문 실행
6. 결과 Supabase 저장
```

## 💰 비용 구조

### 무료 티어
- **Vercel**: 개인 프로젝트 무료
- **Railway**: 월 500시간 무료 ($5 크레딧)
- **Supabase**: 500MB DB, 2GB 스토리지 무료

### 유료 티어 (필요시)
- **Vercel Pro**: $20/월
- **Railway**: $5~20/월
- **Supabase Pro**: $25/월

## 🚀 실제 배포 명령어

### 1. GitHub 준비
```bash
# 로컬에서
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourname/auto-stock.git
git push -u origin main
```

### 2. Railway 배포
```
1. railway.app 접속
2. "New Project" 클릭
3. "Deploy from GitHub" 선택
4. Repository 선택
5. 환경 변수 입력:
   - SUPABASE_URL
   - SUPABASE_KEY
6. "Deploy" 클릭
```

### 3. Vercel 배포
```
1. vercel.com 접속
2. "Import Project" 클릭
3. GitHub repo 선택
4. 환경 변수 입력:
   - REACT_APP_API_URL = https://your-api.railway.app
5. "Deploy" 클릭
```

## ✅ 연결 확인

### Railway 로그 확인
```bash
# Railway CLI
railway logs

# 또는 Dashboard에서 Logs 탭
```

### API 테스트
```bash
# Railway API 테스트
curl https://your-api.railway.app/health

# 응답
{"status": "healthy", "timestamp": "2024-01-01T09:00:00"}
```

### Vercel 사이트 확인
```
https://your-site.vercel.app 접속
→ 로그인
→ 전략 생성 테스트
→ Supabase에서 데이터 확인
```

## 🔧 트러블슈팅

### CORS 에러
```python
# Railway (api_server.py)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-site.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 환경 변수 못 찾음
```python
# Railway에서 반드시 설정
import os
if not os.getenv('SUPABASE_URL'):
    raise ValueError("SUPABASE_URL not set!")
```

### 연결 타임아웃
```javascript
// Vercel (frontend)
const response = await fetch(API_URL, {
  timeout: 30000,  // 30초
  retry: 3
});
```

## 📝 체크리스트

- [ ] GitHub에 코드 업로드
- [ ] Railway 계정 생성
- [ ] Railway에 Python 배포
- [ ] Railway 환경 변수 설정
- [ ] Vercel 계정 생성
- [ ] Vercel에 React 배포
- [ ] Vercel 환경 변수 설정
- [ ] Supabase 테이블 생성
- [ ] API 연결 테스트
- [ ] 전체 플로우 테스트