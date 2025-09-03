# 🔄 Python 파일이 웹에서 작동하는 방식

## 현재 상황 (로컬 개발)
```
[당신의 컴퓨터]
├── Python 파일들 (backend/)
├── React 웹사이트 (frontend/)
└── 로컬에서만 작동 ❌
```

## 실제 배포 후 작동 방식

### 📱 시나리오: 김씨가 스마트폰으로 접속

```
[김씨 스마트폰] 
    ↓ (1. 웹사이트 접속)
[Vercel/Netlify - React 앱]
    ↓ (2. API 요청)
[Railway/AWS - Python 서버] ← 24시간 실행 중!
    ↓ (3. 전략 실행)
[Supabase - 데이터베이스]
```

## 🚀 실제 배포 과정

### 1단계: Python 백엔드를 클라우드에 배포

#### Option A: Railway 사용 (가장 쉬움)
```bash
# 1. Railway 계정 생성 (railway.app)
# 2. GitHub에 코드 업로드
# 3. Railway에서 GitHub 연결
# 4. 자동 배포!
```

#### Railway 배포 파일
```python
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python api_server.py"
  }
}
```

#### 배포 후 상태:
- URL: `https://your-app.railway.app`
- 상태: 24/7 실행 중
- 비용: 월 $5~20

### 2단계: 환경 변수 설정
```python
# Railway 대시보드에서 설정
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
OPENAPI_KEY=한국투자_앱키
OPENAPI_SECRET=한국투자_시크릿
```

### 3단계: 프론트엔드 API URL 변경
```javascript
// frontend/.env.production
REACT_APP_API_URL=https://your-app.railway.app

// frontend/src/config.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## 🔄 실제 실행 흐름

### 1. 사용자가 전략 생성 (웹/모바일)
```javascript
// 프론트엔드 (브라우저에서 실행)
const createStrategy = async () => {
  const response = await fetch('https://your-app.railway.app/api/strategy', {
    method: 'POST',
    body: JSON.stringify({
      name: "나의 전략",
      indicators: { rsi: { enabled: true } }
    })
  });
};
```

### 2. Python 서버가 요청 처리 (클라우드에서 실행)
```python
# api_server.py (Railway 서버에서 24/7 실행 중)
@app.post("/api/strategy")
async def create_strategy(request):
    # 1. 요청 받음
    strategy_data = request.json()
    
    # 2. Supabase에 저장
    supabase.table('strategies').insert(strategy_data).execute()
    
    # 3. 응답 전송
    return {"success": True}
```

### 3. 자동 매매 실행 (클라우드에서 실행)
```python
# cloud_executor.py (Railway에서 24/7 실행)
while True:
    # 매분마다 실행
    if is_market_open():
        # 1. 모든 활성 전략 조회
        strategies = supabase.table('strategies').select('*').eq('is_active', True)
        
        # 2. 각 전략 실행
        for strategy in strategies:
            # 한국투자 API 호출
            market_data = fetch_market_data(strategy['universe'])
            
            # 전략 계산
            signal = calculate_strategy(market_data, strategy)
            
            # 주문 실행
            if signal == 'BUY':
                place_order(...)
    
    time.sleep(60)  # 1분 대기
```

## 📱 다양한 기기에서 접속 시

### 김씨가 회사 컴퓨터에서:
1. `https://your-site.com` 접속
2. 로그인
3. 전략 설정 변경
4. **Python 서버(클라우드)**가 처리
5. Supabase에 저장

### 박씨가 해외에서 스마트폰으로:
1. 동일한 사이트 접속
2. 로그인
3. 실시간 수익 확인
4. **같은 Python 서버**가 데이터 제공

### 이씨가 태블릿에서:
1. 전략 백테스트 실행
2. **Python 서버**가 계산
3. 결과 확인

## 🎯 핵심 포인트

### 로컬 vs 프로덕션
```
로컬 (개발):
- Python: localhost:8000 (내 컴퓨터)
- React: localhost:3000 (내 컴퓨터)
- 다른 사람 접속 ❌

프로덕션 (배포):
- Python: railway.app (클라우드 24/7)
- React: vercel.app (클라우드 CDN)
- 전 세계 접속 ✅
```

## 💰 비용

### 무료 옵션:
- Vercel (프론트엔드): 무료
- Supabase (DB): 무료 (제한 있음)
- Render.com (백엔드): 무료 (제한 있음)

### 유료 옵션 (안정적):
- Railway (백엔드): $5-20/월
- Supabase Pro: $25/월
- 총: 약 $30/월 (4만원)

## 🔧 실제 배포 명령어

### 1. GitHub에 코드 업로드
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Railway 배포
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 생성
railway init

# 배포
railway up
```

### 3. 환경 변수 설정
```bash
railway variables set SUPABASE_URL=https://xxx.supabase.co
railway variables set SUPABASE_KEY=your-key
```

### 4. 확인
```bash
railway logs  # 로그 확인
railway open  # 브라우저에서 열기
```

## ✅ 배포 완료 후

이제 전 세계 어디서든:
1. 웹사이트 접속 가능
2. Python 코드가 클라우드에서 실행
3. 자동매매 24/7 작동
4. 모든 기기에서 동일하게 작동

## 🤔 추가 질문

Q: Python 파일을 수정하면?
A: GitHub에 push → Railway 자동 재배포

Q: 서버가 죽으면?
A: Railway가 자동 재시작

Q: 많은 사용자가 접속하면?
A: 자동 스케일링 (또는 더 큰 서버로 업그레이드)