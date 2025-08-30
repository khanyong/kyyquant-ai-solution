import { boardService } from './boardService'

export const initializeNotices = async () => {
  try {
    // 공지사항 게시판에 기존 게시글이 있는지 확인
    const { posts } = await boardService.getPosts('notice', { limit: 1 })
    
    // 이미 게시글이 있으면 초기화하지 않음
    if (posts.length > 0) {
      console.log('Notices already initialized')
      return
    }

    // 1. 프로젝트 개요 공지
    await boardService.createPost('notice', {
      title: '🚀 KyyQuant AI Solution 개발 계획',
      content: `KyyQuant AI Solution은 AI 기반 자동매매 플랫폼 구축 프로젝트입니다.

## 프로젝트 진행 현황
- 전체 진행률: 약 40%
- 완료된 작업: 6개
- 진행 중인 작업: 2개
- 대기 중인 작업: 7개

## 주요 기능
- AI 기반 알고리즘 트레이딩
- 보조지표 기반 자동매매
- 백테스팅 & 최적화
- 실시간 신호 모니터링
- 포트폴리오 관리
- 리스크 관리 시스템

## 최근 완료된 기능
✅ Supabase 인증 시스템 완성 (소셜 로그인, 프로필 관리)
✅ 전략 빌더 고도화 (일목균형표, 리스크 관리 슬라이더)
✅ 백테스팅 시스템 Supabase 연동 완료
✅ 투자 설정 시스템 구현 (업종지표, 분할매매, 시스템 CUT)
✅ 커뮤니티 게시판 시스템 구축

## 현재 진행 중인 작업
💡 Task #7: 실시간 대시보드 - WebSocket 연동 및 실시간 차트
💡 Task #8: 자동매매 시스템 - 키움 API 서버 연동`,
      category: '공지',
      tags: ['프로젝트', '개발현황', 'KyyQuant'],
      is_notice: true,
      is_pinned: true
    })

    // 2. 개발 로드맵 공지
    await boardService.createPost('notice', {
      title: '📋 개발 로드맵',
      content: `## Phase 1: 기초 시스템 구축 (완료)
✅ Task #1: 프로젝트 초기 설정
- React + Vite 프로젝트 초기화
- TypeScript 설정
- Material-UI 테마 설정
- Redux Toolkit 상태관리 구성

✅ Task #2: 데이터베이스 스키마 설계
- 사용자 프로필, 전략, 백테스팅 테이블
- 섹터 성과, 리스크 지표 테이블
- 투자 설정 테이블

✅ Task #3: Supabase 인증 시스템
- Supabase Auth 연동
- 로그인/회원가입 UI 구현
- 소셜 로그인 (Google, GitHub)
- 관리자 권한 시스템

## Phase 2: 핵심 기능 개발 (완료)
✅ Task #4: 전략 빌더 시스템
- 보조지표 선택 UI (RSI, MACD, BB, MA, 일목균형표 등)
- 조건 설정 인터페이스
- 전략 저장/불러오기 기능

✅ Task #5: 백테스팅 시스템
- Supabase 백테스팅 데이터 연동
- 수익률 곡선 차트
- 리스크 분석
- 섹터별 성과 분석

✅ Task #6: 투자 설정 시스템
- 투자 유니버스 설정
- 매매 조건 상세 설정
- 포트폴리오 관리 설정

## Phase 3: 실시간 트레이딩 (진행중)
⏳ Task #7: 실시간 대시보드 개발
- 시장 개요 위젯
- 포트폴리오 현황
- 실시간 시세 WebSocket 연동

⏳ Task #8: 자동매매 시스템
- 자동매매 UI 패널
- 키움 API 연동 서버
- 실시간 주문 실행

## Phase 4: 고급 기능 (예정)
📌 Task #9: 실시간 신호 모니터링
📌 Task #10: 성과 분석 대시보드
📌 Task #11: AI 포트폴리오 최적화
📌 Task #12: 알림 시스템

## Phase 5: 최적화 및 배포 (예정)
📌 Task #13: 모바일 반응형 UI
📌 Task #14: 테스트 및 최적화
📌 Task #15: 문서화 및 배포`,
      category: '공지',
      tags: ['로드맵', '개발계획', '진행상황'],
      is_notice: true
    })

    // 3. 기술 스택 공지
    await boardService.createPost('notice', {
      title: '🛠️ 기술 스택',
      content: `## Frontend
- **React 18**: 사용자 인터페이스 구축
- **TypeScript**: 타입 안정성
- **Vite**: 빌드 도구
- **Material-UI v5**: UI 컴포넌트 라이브러리
- **Redux Toolkit**: 상태 관리
- **Chart.js**: 차트 라이브러리
- **React Router v6**: 라우팅

## Backend & Database
- **Supabase**: Backend as a Service
  - PostgreSQL 데이터베이스
  - 실시간 구독
  - 인증 시스템
  - Row Level Security
- **Supabase Auth**: 사용자 인증
- **Supabase Realtime**: 실시간 데이터 동기화

## Trading System (개발 예정)
- **Python**: 백엔드 개발 언어
- **FastAPI**: REST API 프레임워크
- **키움 OpenAPI**: 증권 거래 API
- **WebSocket**: 실시간 통신
- **Redis**: 캐싱 및 세션 관리

## DevOps & Deployment
- **Vercel**: 프론트엔드 호스팅
- **GitHub Actions**: CI/CD
- **Docker**: 컨테이너화 (예정)

## 개발 도구
- **VS Code**: 코드 에디터
- **Git**: 버전 관리
- **ESLint & Prettier**: 코드 품질 관리
- **Postman**: API 테스트`,
      category: '공지',
      tags: ['기술스택', '개발환경', 'Tech'],
      is_notice: true
    })

    // 4. 커뮤니티 이용 안내
    await boardService.createPost('notice', {
      title: '📢 커뮤니티 이용 안내',
      content: `KyyQuant AI Solution 커뮤니티에 오신 것을 환영합니다!

## 게시판 소개

### 1. 공지사항
- 시스템 업데이트 및 중요 공지
- 개발 진행 상황 공유
- 서비스 점검 안내

### 2. 자유게시판
- 자유로운 소통 공간
- 투자 관련 정보 공유
- 일상 대화

### 3. Q&A
- 시스템 사용법 질문
- 투자 전략 질문
- 기술적 문의사항

### 4. 전략 공유
- 투자 전략 공유
- 백테스팅 결과 공유
- 전략 아이디어 토론

### 5. 시장 분석
- 시장 동향 분석
- 종목 분석 리포트
- 경제 지표 분석

### 6. 백테스트 결과
- 백테스팅 결과 공유
- 성과 분석
- 전략 비교

## 이용 규칙

1. **상호 존중**: 모든 회원을 존중하며 예의를 지켜주세요
2. **정확한 정보**: 검증된 정보만 공유해주세요
3. **저작권 준수**: 타인의 저작물을 무단으로 사용하지 마세요
4. **광고 금지**: 상업적 광고나 스팸은 금지됩니다
5. **개인정보 보호**: 개인정보를 함부로 공개하지 마세요

## 회원 등급

### 일반 회원 (User)
- 기본 게시판 이용 가능
- 글 작성 및 댓글 작성 가능

### 프리미엄 회원 (Premium)
- 프리미엄 전략 게시판 이용 가능
- 고급 분석 자료 열람 가능
- 우선 지원 서비스

### VIP 회원
- 모든 게시판 무제한 이용
- 1:1 컨설팅 서비스
- 독점 전략 제공

### 관리자 (Admin)
- 게시판 관리
- 회원 관리
- 시스템 관리

## 문의사항
- 이메일: support@kyyquant.com
- 카카오톡: @kyyquant
- 운영시간: 평일 09:00 ~ 18:00

감사합니다.
KyyQuant AI Solution 운영팀`,
      category: '공지',
      tags: ['이용안내', '규칙', '커뮤니티'],
      is_notice: true,
      is_pinned: true
    })

    // 5. 자유게시판에 환영 게시글
    await boardService.createPost('free', {
      title: '커뮤니티 오픈을 축하합니다! 🎉',
      content: `안녕하세요, KyyQuant AI Solution 커뮤니티가 드디어 오픈했습니다!

이제 여러분들과 투자 전략, 시장 분석, 그리고 다양한 이야기를 나눌 수 있게 되어 기쁩니다.

앞으로 많은 참여와 활발한 소통 부탁드립니다.

함께 성장하는 커뮤니티가 되었으면 좋겠습니다! 💪`,
      category: '일반',
      tags: ['환영', '오픈', '인사']
    })

    // 6. Q&A에 FAQ 게시글
    await boardService.createPost('qna', {
      title: '[FAQ] 자주 묻는 질문 모음',
      content: `## Q1. KyyQuant AI Solution은 무엇인가요?
**A:** AI 기반 알고리즘 트레이딩 플랫폼으로, 자동매매 전략을 구축하고 백테스팅할 수 있는 서비스입니다.

## Q2. 어떤 지표들을 사용할 수 있나요?
**A:** RSI, MACD, 볼린저밴드, 이동평균선, 일목균형표 등 다양한 기술적 지표를 지원합니다.

## Q3. 백테스팅은 어떻게 하나요?
**A:** 전략 빌더에서 전략을 구성한 후, 백테스팅 탭에서 기간을 설정하고 실행하면 됩니다.

## Q4. 실제 매매는 가능한가요?
**A:** 현재 키움증권 API 연동을 개발 중이며, 곧 실제 매매가 가능해질 예정입니다.

## Q5. 프리미엄 회원의 혜택은 무엇인가요?
**A:** 프리미엄 전략 열람, 고급 분석 도구, 우선 지원 등의 혜택이 있습니다.

## Q6. 모바일에서도 사용 가능한가요?
**A:** 현재 모바일 반응형 UI를 개발 중이며, 곧 모바일에서도 편리하게 사용하실 수 있습니다.

추가 질문이 있으시면 언제든지 문의해주세요!`,
      category: '질문',
      tags: ['FAQ', '가이드', '도움말']
    })

    console.log('Notices initialized successfully')
  } catch (error) {
    console.error('Failed to initialize notices:', error)
  }
}

// 초기 데이터 생성 함수
export const createInitialPosts = async () => {
  // 전략 공유 게시판에 샘플 게시글
  try {
    await boardService.createPost('strategy_share', {
      title: 'RSI + MACD 조합 전략 공유',
      content: `제가 사용하는 RSI + MACD 조합 전략을 공유합니다.

## 전략 개요
- RSI 30 이하에서 MACD 골든크로스 시 매수
- RSI 70 이상에서 MACD 데드크로스 시 매도

## 백테스팅 결과
- 기간: 2023.01 ~ 2023.12
- 수익률: +32.5%
- 최대낙폭: -8.2%
- 승률: 68%

## 주의사항
- 변동성이 큰 종목에서는 손절 기준을 엄격히 적용
- 시장 전체가 하락 추세일 때는 사용 자제

참고하시고 좋은 결과 있으시길 바랍니다!`,
      category: '전략',
      tags: ['RSI', 'MACD', '전략공유']
    })

    await boardService.createPost('market_analysis', {
      title: '2024년 하반기 시장 전망',
      content: `## 2024년 하반기 주요 이슈

### 1. 금리 인하 가능성
- 연준의 금리 인하 시그널 주목
- 인하 시기와 폭이 관건

### 2. AI 섹터 전망
- 생성형 AI 관련주 강세 지속 예상
- 반도체 섹터 동반 상승 가능성

### 3. 국내 시장
- 외국인 수급 개선 여부가 중요
- 배당주 및 가치주 관심 증가

### 4. 리스크 요인
- 지정학적 리스크 지속
- 중국 경제 둔화 우려

## 투자 전략
- 분산 투자로 리스크 관리
- 장기 성장주 + 배당주 조합
- 현금 비중 20% 이상 유지 권장`,
      category: '분석',
      tags: ['시장전망', '2024', '투자전략']
    })
  } catch (error) {
    console.error('Failed to create initial posts:', error)
  }
}