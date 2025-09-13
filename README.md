# KyyQuant AI Solution

AI 기반 퀀트 투자 자동화 솔루션

## 📋 프로젝트 개요

KyyQuant AI Solution은 주식 투자 전략을 자동화하고 백테스트할 수 있는 종합 투자 플랫폼입니다.

### 주요 기능
- 📊 **투자 유니버스 필터링**: 다양한 재무지표 기반 종목 선정
- 🎯 **전략 빌더**: 매매 규칙 및 조건 설정
- 📈 **백테스트 시스템**: 과거 데이터 기반 전략 검증
- ☁️ **클라우드 저장**: 필터 및 전략 영구 보관
- 🔄 **실시간 모니터링**: 투자 성과 추적

## 🚀 시작하기

### 필수 요구사항
- Node.js 18.0 이상
- npm 또는 yarn
- 최신 브라우저 (Chrome, Edge 권장)

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/yourusername/auto_stock.git
cd auto_stock
```

2. **의존성 설치**
```bash
npm install
```

3. **환경 변수 설정**
`.env` 파일을 프로젝트 루트에 생성하고 아래 내용을 추가합니다:

```env
# Supabase 설정 (필수)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# 백테스트 서버 설정
# 로컬 개발 (기본값)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# 원격 백테스트 서버 사용 시 (예: 다른 PC)
# VITE_API_URL=http://192.168.1.100:8000
# VITE_WS_URL=ws://192.168.1.100:8000/ws

# 클라우드 서버 사용 시
# VITE_API_URL=https://api.kyyquant.com
# VITE_WS_URL=wss://api.kyyquant.com/ws
```

4. **개발 서버 시작**
```bash
npm run dev
```

## 🔧 백테스트 서버 설정

### 로컬 백테스트 서버
백테스트 기능을 사용하려면 별도의 백엔드 서버가 필요합니다.

```bash
# 백엔드 서버 저장소 (별도 제공)
cd backend
pip install -r requirements.txt
python main.py
```

### 원격 백테스트 서버 연결

다른 컴퓨터에서 백테스트를 실행하려면:

1. **백엔드 서버 PC에서:**
   - 백엔드 서버를 0.0.0.0으로 바인딩하여 실행
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   - 방화벽에서 8000 포트 허용

2. **클라이언트 PC에서:**
   - `.env` 파일 수정
   ```env
   VITE_API_URL=http://서버PC_IP주소:8000
   VITE_WS_URL=ws://서버PC_IP주소:8000/ws
   ```
   - 예시:
   ```env
   VITE_API_URL=http://192.168.1.100:8000
   VITE_WS_URL=ws://192.168.1.100:8000/ws
   ```

3. **개발 서버 재시작**
   ```bash
   npm run dev
   ```

## 📚 사용 가이드

### 빠른 시작
1. [투자설정](docs/guides/BACKTEST_GUIDE.md#1-투자설정---유니버스-필터링) - 종목 필터링
2. [전략빌더](docs/guides/BACKTEST_GUIDE.md#2-전략빌더---매매-전략-생성) - 매매 전략 생성
3. [백테스트](docs/guides/BACKTEST_GUIDE.md#3-백테스트---전략-검증) - 전략 검증

### 상세 문서
- [백테스트 가이드](docs/guides/BACKTEST_GUIDE.md) - 전체 기능 상세 설명
- [개발 로드맵](docs/development/DEVELOPMENT_ROADMAP.md) - 프로젝트 진행 상황
- [투자 데이터 수집](docs/guides/INVESTMENT_DATA_COLLECTION_GUIDE.md) - 데이터 수집 방법

## 🏗️ 프로젝트 구조

```
auto_stock/
├── src/                 # 소스 코드
│   ├── components/      # React 컴포넌트
│   ├── services/        # API 및 서비스
│   ├── lib/            # 외부 라이브러리 설정
│   └── types/          # TypeScript 타입 정의
├── backend/            # 백엔드 서버
├── docs/               # 문서
│   ├── deployment/     # 배포 관련 문서
│   ├── development/    # 개발 관련 문서
│   ├── guides/         # 사용 가이드
│   ├── api/           # API 문서
│   └── system/        # 시스템 문서
├── scripts/           # 유틸리티 스크립트
├── n8n_workflows/     # n8n 워크플로우
├── supabase/          # Supabase 설정
└── data/              # 데이터 파일
```

## 🛠️ 기술 스택

- **Frontend**: React, TypeScript, MUI
- **State Management**: Zustand
- **Database**: Supabase (PostgreSQL)
- **Build Tool**: Vite
- **Styling**: Emotion, MUI

## 🐛 문제 해결

### 백테스트 서버 연결 실패
- 백엔드 서버가 실행 중인지 확인
- `.env` 파일의 `VITE_API_URL` 확인
- 네트워크 연결 및 방화벽 설정 확인

### 종목 데이터 로드 실패
- Supabase 연결 설정 확인
- 데이터베이스 테이블 존재 여부 확인
- API 키 유효성 확인

### 필터 저장/불러오기 실패
- 로그인 상태 확인 (클라우드 저장 시)
- 브라우저 쿠키/캐시 정리
- 로컬 스토리지 용량 확인

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 🤝 기여하기

기여를 환영합니다! Pull Request를 보내주세요.

## 📞 지원

- 이슈 트래커: [GitHub Issues](https://github.com/yourusername/auto_stock/issues)
- 이메일: support@kyyquant.com

---

*Version 2.0.0 - 백테스트 필터링 시스템 추가*