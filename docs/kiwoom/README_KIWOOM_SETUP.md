# 키움증권 API 연동 가이드

## 📋 사전 준비사항

1. **키움증권 계좌 개설**
   - 키움증권 홈페이지에서 계좌 개설
   - 공인인증서 발급

2. **키움 OpenAPI+ 설치**
   - [키움증권 OpenAPI+](https://www.kiwoom.com/h/customer/download/VOpenApiInfoView) 다운로드
   - KOA Studio 설치 (API 테스트 도구)
   - 모의투자 신청 (테스트용)

## 🚀 설치 및 실행

### 1. Windows 서버 환경 설정

```bash
# backend 폴더로 이동
cd backend

# 설치 스크립트 실행
setup_windows.bat

# Python 패키지 수동 설치 (필요시)
pip install -r requirements.txt
```

### 2. 환경변수 설정

#### Backend (.env 파일)
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Kiwoom Account
KIWOOM_ACCOUNT_NO=your_account_number
KIWOOM_PASSWORD=your_password
KIWOOM_CERT_PASSWORD=your_cert_password
```

#### Frontend (.env.local 파일)
```env
# Supabase
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Kiwoom WebSocket
VITE_KIWOOM_WS_URL=ws://localhost:8765

# Backend API
VITE_API_URL=http://localhost:8000
```

### 3. Supabase 데이터베이스 설정

1. Supabase 프로젝트에서 SQL Editor 열기
2. `supabase/migrations/create_kiwoom_tables.sql` 실행
3. Realtime 설정 확인

### 4. 서버 실행

#### Windows 서버 (키움 API 브리지)
```bash
# backend 폴더에서
python kiwoom_bridge_server.py
```

#### 개발 서버 (Frontend)
```bash
# 프로젝트 루트에서
npm run dev
```

## 📊 아키텍처

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  키움 OpenAPI+  │────▶│  WebSocket      │────▶│    Supabase     │
│  (Windows)      │     │  Bridge Server  │     │    Database     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                         │
                              ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   React App     │────▶│  Supabase       │
                        │   (Frontend)    │     │  Realtime       │
                        └─────────────────┘     └─────────────────┘
```

## 🔧 주요 기능

### 실시간 데이터
- 실시간 주식 시세
- 포트폴리오 자동 업데이트
- 주문 체결 알림

### 주문 기능
- 지정가/시장가 주문
- 매수/매도 주문
- 주문 취소 및 정정

### 데이터 저장
- 실시간 가격 데이터
- 일봉/분봉 차트 데이터
- 거래 내역 자동 저장

## 📝 사용 방법

### 1. 대시보드 접속
```
http://localhost:5173/kiwoom
```

### 2. 관심종목 추가
```typescript
// KiwoomService 사용 예시
import kiwoomService from './services/kiwoomService'

// 관심종목 추가
await kiwoomService.addToWatchlist('005930', '삼성전자', 70000)

// 실시간 구독
kiwoomService.subscribeStock('005930')
```

### 3. 주문 실행
```typescript
// 매수 주문
await kiwoomService.sendOrder({
  stock_code: '005930',
  stock_name: '삼성전자',
  order_type: 'BUY',
  order_method: 'LIMIT',
  quantity: 10,
  price: 70000,
  status: 'PENDING'
})
```

## 🔍 트러블슈팅

### WebSocket 연결 실패
- Windows 방화벽에서 8765 포트 허용
- 키움 OpenAPI+ 로그인 상태 확인

### 실시간 데이터 수신 안됨
- 키움증권 실시간 조회 제한 확인 (종목당 5개)
- WebSocket 연결 상태 확인

### Supabase 연동 문제
- RLS 정책 확인
- Realtime 구독 설정 확인

## 📌 주의사항

1. **실전/모의투자 구분**
   - 개발 중에는 반드시 모의투자 계좌 사용
   - 실전 투자 전 충분한 테스트 필수

2. **API 제한사항**
   - 1초당 최대 5회 조회 제한
   - 동시 실시간 조회 종목 200개 제한

3. **보안**
   - 절대 인증 정보를 코드에 하드코딩하지 않기
   - .env 파일은 반드시 .gitignore에 포함

## 📚 참고 자료

- [키움 OpenAPI+ 개발가이드](https://download.kiwoom.com/web/openapi/kiwoom_openapi_plus_devguide_ver_1.5.pdf)
- [Supabase Realtime 문서](https://supabase.com/docs/guides/realtime)
- [PyQt5 문서](https://www.riverbankcomputing.com/static/Docs/PyQt5/)