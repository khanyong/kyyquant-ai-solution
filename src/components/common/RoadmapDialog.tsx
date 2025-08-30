import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Stack,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Close,
  CheckCircle,
  Schedule,
  Assignment,
  Code,
  Storage,
  Security,
  Dashboard,
  Assessment,
  TrendingUp,
  AutoGraph,
  Notifications,
  BugReport,
  Description,
  Settings,
  ExpandMore,
  Forum
} from '@mui/icons-material'

interface RoadmapDialogProps {
  open: boolean
  onClose: () => void
}

const RoadmapDialog: React.FC<RoadmapDialogProps> = ({ open, onClose }) => {
  const tasks = [
    {
      id: 1,
      title: 'KyyQuant AI Solution 프로젝트 초기 설정',
      status: 'done',
      priority: 'high',
      icon: <Assignment />,
      period: '2024.08.25 - 2024.08.26',
      description: 'React 18 + Vite + TypeScript 기반의 모던 웹 애플리케이션 프로젝트 초기 구성',
      subtasks: [
        {
          title: '✅ React + Vite 프로젝트 초기화',
          details: [
            'Vite 4.5 빌드 도구 설정',
            'React 18.2 설치 및 구성',
            'Hot Module Replacement (HMR) 설정',
            'ESLint, Prettier 코드 품질 도구 구성',
            '개발 서버 포트 3000 설정'
          ]
        },
        {
          title: '✅ TypeScript 설정',
          details: [
            'TypeScript 5.0 설치',
            'tsconfig.json 구성 (strict mode 활성화)',
            'Path alias 설정 (@components, @services 등)',
            '타입 정의 파일 구조 설계',
            'Custom hooks 타입 정의'
          ]
        },
        {
          title: '✅ Material-UI 테마 설정',
          details: [
            'MUI v5.14 설치 및 설정',
            '다크 테마 커스터마이징',
            'Pretendard 폰트 적용',
            '색상 팔레트 정의 (primary: #90caf9, secondary: #f48fb1)',
            '반응형 브레이크포인트 설정'
          ]
        },
        {
          title: '✅ Redux Toolkit 상태관리 구성',
          details: [
            'Redux Toolkit 1.9 설치',
            'Store 구조 설계 (auth, market, strategy, trading)',
            'Redux DevTools 연동',
            'Redux Persist 로컬 스토리지 연동',
            'Async thunk 미들웨어 설정'
          ]
        },
        {
          title: '✅ 라우팅 시스템 구축',
          details: [
            'React Router v6 설치',
            '중첩 라우팅 구조 설계',
            'Protected routes 구현',
            'Layout 컴포넌트 구조화',
            '404 페이지 처리'
          ]
        }
      ]
    },
    {
      id: 2,
      title: '데이터베이스 스키마 설계 및 구현',
      status: 'done',
      priority: 'high',
      icon: <Storage />,
      period: '2024.08.26 - 2024.08.28',
      description: 'Supabase PostgreSQL 데이터베이스 설계 및 Row Level Security 구현',
      subtasks: [
        {
          title: '✅ 사용자 관리 테이블',
          details: [
            'profiles 테이블: 사용자 프로필 정보 (id, name, email, role, created_at)',
            'roles 테이블: 역할 정의 (admin, user, premium, vip)',
            'user_permissions 테이블: 세부 권한 관리',
            'user_settings 테이블: 사용자별 설정 저장',
            'RLS 정책: 본인 프로필만 수정 가능'
          ]
        },
        {
          title: '✅ 전략 관리 테이블',
          details: [
            'strategies 테이블: 전략 기본 정보',
            'strategy_conditions 테이블: 전략 조건 상세',
            'strategy_indicators 테이블: 사용 지표 정보',
            'strategy_parameters 테이블: 파라미터 값',
            'strategy_versions 테이블: 버전 관리'
          ]
        },
        {
          title: '✅ 백테스팅 결과 테이블',
          details: [
            'backtest_results 테이블: 백테스트 요약 정보',
            'backtest_trades 테이블: 개별 거래 내역',
            'daily_returns 테이블: 일별 수익률',
            'monthly_returns 테이블: 월별 수익률',
            'sector_performance 테이블: 섹터별 성과',
            'risk_metrics 테이블: 리스크 지표 (샤프지수, 최대낙폭 등)'
          ]
        },
        {
          title: '✅ 게시판 시스템 테이블',
          details: [
            'board_categories 테이블: 게시판 카테고리',
            'boards 테이블: 게시판 정의 (8개 기본 게시판)',
            'posts 테이블: 게시글 (제목, 내용, 조회수, 좋아요)',
            'comments 테이블: 댓글 및 대댓글',
            'attachments 테이블: 첨부파일',
            'reactions 테이블: 좋아요/싫어요',
            'board_permissions 테이블: 게시판별 권한'
          ]
        },
        {
          title: '✅ 투자 설정 테이블',
          details: [
            'investment_settings 테이블: 사용자별 투자 설정',
            'universe_filters 테이블: 종목 필터링 조건',
            'portfolio_settings 테이블: 포트폴리오 구성',
            'risk_settings 테이블: 리스크 관리 설정',
            'trading_rules 테이블: 매매 규칙'
          ]
        }
      ]
    },
    {
      id: 3,
      title: 'Supabase 인증 시스템 구현',
      status: 'done',
      priority: 'high',
      icon: <Security />,
      period: '2024.08.28 - 2024.08.29',
      description: 'Supabase Auth를 활용한 완전한 인증/인가 시스템 구축',
      subtasks: [
        {
          title: '✅ Supabase Auth 연동',
          details: [
            'Supabase 프로젝트 생성 및 환경변수 설정',
            'Auth 클라이언트 초기화',
            'JWT 토큰 관리 시스템',
            '세션 자동 갱신 로직',
            'Auth 상태 전역 관리 (Redux)'
          ]
        },
        {
          title: '✅ 로그인/회원가입 UI 구현',
          details: [
            'LoginDialog 컴포넌트 개발',
            '이메일/비밀번호 로그인 폼',
            '회원가입 폼 및 유효성 검증',
            '비밀번호 찾기 기능',
            '이메일 인증 플로우'
          ]
        },
        {
          title: '✅ 소셜 로그인 구현',
          details: [
            'Google OAuth 2.0 연동',
            'GitHub OAuth 연동',
            'OAuth 콜백 처리',
            '소셜 계정 프로필 동기화',
            '중복 계정 병합 로직'
          ]
        },
        {
          title: '✅ 세션 관리 시스템',
          details: [
            '자동 로그인 구현 (Remember Me)',
            '세션 만료 처리',
            'Refresh token 자동 갱신',
            '다중 디바이스 세션 관리',
            '로그아웃 시 세션 정리'
          ]
        },
        {
          title: '✅ 관리자 권한 시스템',
          details: [
            'Role-based access control (RBAC)',
            'Protected routes 구현',
            '관리자 전용 UI 컴포넌트',
            '권한별 메뉴 표시/숨김',
            'API 레벨 권한 검증'
          ]
        }
      ]
    },
    {
      id: 4,
      title: '전략 빌더 시스템 개발',
      status: 'done',
      priority: 'high',
      icon: <Code />,
      period: '2024.08.29 - 2024.08.30',
      description: '드래그 앤 드롭 기반의 직관적인 투자 전략 구성 시스템',
      subtasks: [
        {
          title: '✅ 보조지표 선택 UI',
          details: [
            'RSI (14, 28일) 지표 구현',
            'MACD (12, 26, 9) 지표 구현',
            '볼린저밴드 (20일, 2σ) 구현',
            '이동평균선 (5, 20, 60, 120일) 구현',
            '일목균형표 (전환선, 기준선, 구름대) 구현',
            'Stochastic, CCI, Williams %R 추가'
          ]
        },
        {
          title: '✅ 조건 설정 인터페이스',
          details: [
            'AND/OR 로직 게이트 구현',
            '중첩 조건 그룹 지원',
            '비교 연산자 선택 (>, <, =, ≥, ≤)',
            '크로스오버/언더 조건',
            '다중 타임프레임 조건'
          ]
        },
        {
          title: '✅ 일목균형표 특수 조건',
          details: [
            '구름대 돌파 매매 신호',
            '전환선/기준선 교차 신호',
            '후행스팬 확인 로직',
            '삼역전환 패턴 인식',
            '구름대 두께 기반 신호 강도'
          ]
        },
        {
          title: '✅ 리스크 관리 설정',
          details: [
            '손절매 설정 (고정%, ATR 기반)',
            '익절매 설정 (목표 수익률)',
            '트레일링 스톱 구현',
            '포지션 크기 계산기',
            '최대 손실 한도 설정'
          ]
        },
        {
          title: '✅ 전략 저장/관리',
          details: [
            'Supabase 전략 저장',
            '전략 버전 관리',
            '전략 공유 기능',
            '전략 템플릿 라이브러리',
            'JSON 내보내기/가져오기'
          ]
        }
      ]
    },
    {
      id: 5,
      title: '백테스팅 시스템 구현',
      status: 'done',
      priority: 'high',
      icon: <Assessment />,
      period: '2024.08.30',
      description: '과거 데이터 기반 전략 성과 검증 및 분석 시스템',
      subtasks: [
        {
          title: '✅ 백테스팅 엔진',
          details: [
            '틱 데이터 기반 시뮬레이션',
            '슬리피지 및 수수료 반영',
            '부분 체결 시뮬레이션',
            '시장가/지정가 주문 처리',
            '거래량 제약 반영'
          ]
        },
        {
          title: '✅ 성과 분석 차트',
          details: [
            'Chart.js 기반 수익률 곡선',
            '누적 수익률 차트',
            '일별/월별 수익률 히트맵',
            '드로우다운 차트',
            '벤치마크 대비 성과'
          ]
        },
        {
          title: '✅ 리스크 분석',
          details: [
            '샤프 지수 계산',
            '소르티노 지수 계산',
            '최대 낙폭 (MDD) 분석',
            'Value at Risk (VaR)',
            '변동성 분석'
          ]
        },
        {
          title: '✅ 거래 분석',
          details: [
            '승률 및 손익비 계산',
            '평균 보유기간 분석',
            '최대 연속 손실/이익',
            '거래 빈도 분석',
            '종목별 성과 분석'
          ]
        },
        {
          title: '✅ 섹터별 성과',
          details: [
            '섹터 수익률 비교',
            '섹터 로테이션 분석',
            '섹터 상관관계 매트릭스',
            '섹터 집중도 분석',
            '섹터 타이밍 분석'
          ]
        }
      ]
    },
    {
      id: 6,
      title: '커뮤니티 게시판 시스템',
      status: 'done',
      priority: 'high',
      icon: <Forum />,
      period: '2024.08.30',
      description: '사용자 소통을 위한 다기능 게시판 시스템 구축',
      subtasks: [
        {
          title: '✅ 게시판 구조 설계',
          details: [
            '공지사항 게시판 (관리자 전용)',
            '자유게시판 (모든 사용자)',
            'Q&A 게시판 (질문/답변)',
            '전략 공유 게시판',
            '시장 분석 게시판',
            '백테스트 결과 공유',
            '프리미엄 전략 (프리미엄 회원 전용)'
          ]
        },
        {
          title: '✅ 게시글 기능',
          details: [
            'WYSIWYG 에디터 통합',
            '이미지/파일 첨부',
            '코드 하이라이팅',
            '마크다운 지원',
            '임시 저장 기능',
            '비밀글 설정'
          ]
        },
        {
          title: '✅ 댓글 시스템',
          details: [
            '댓글 및 대댓글 구조',
            '실시간 댓글 업데이트',
            '댓글 알림 시스템',
            '댓글 좋아요',
            '베스트 댓글 선정'
          ]
        },
        {
          title: '✅ 상호작용 기능',
          details: [
            '좋아요/싫어요 시스템',
            '조회수 카운팅',
            '북마크 기능',
            '게시글 공유',
            '신고 시스템'
          ]
        },
        {
          title: '✅ 권한 관리',
          details: [
            '게시판별 읽기/쓰기 권한',
            '역할 기반 접근 제어',
            'IP 기반 제한',
            '스팸 방지 시스템',
            '자동 필터링'
          ]
        }
      ]
    },
    {
      id: 7,
      title: '투자 설정 시스템',
      status: 'done',
      priority: 'high',
      icon: <Settings />,
      period: '2024.08.30',
      description: '개인화된 투자 전략 설정 및 관리 시스템',
      subtasks: [
        {
          title: '✅ 투자 유니버스 설정',
          details: [
            '시가총액 필터 (대형주/중형주/소형주)',
            'PER, PBR, ROE 범위 설정',
            '부채비율 필터링',
            '거래량 조건 설정',
            '외국인/기관 보유 비율',
            '투자경고/거래정지 종목 제외'
          ]
        },
        {
          title: '✅ 포트폴리오 관리',
          details: [
            '최대/최소 보유 종목 수',
            '종목당 최대 비중 제한',
            '섹터별 비중 제한',
            '현금 보유 비율',
            '리밸런싱 주기 설정'
          ]
        },
        {
          title: '✅ 매매 조건 설정',
          details: [
            '진입 조건 상세 설정',
            '청산 조건 설정',
            '분할 매수/매도 전략',
            '평균 단가 관리',
            '슬리피지 허용 범위'
          ]
        },
        {
          title: '✅ 위험 관리',
          details: [
            '계좌 전체 손실 한도',
            '일일 손실 한도',
            '종목별 손실 한도',
            '변동성 기반 포지션 조절',
            '시스템 CUT 설정'
          ]
        },
        {
          title: '✅ 업종/테마 설정',
          details: [
            '선호 업종 선택',
            '제외 업종 설정',
            '테마주 필터링',
            '업종 순환 전략',
            '업종 상대강도 분석'
          ]
        }
      ]
    },
    {
      id: 8,
      title: '실시간 대시보드 개발',
      status: 'in-progress',
      priority: 'high',
      icon: <Dashboard />,
      period: '2024.08.30 - 진행중',
      description: '실시간 시장 데이터 및 포트폴리오 모니터링 대시보드',
      subtasks: [
        {
          title: '✅ 시장 개요 위젯',
          details: [
            'KOSPI/KOSDAQ 지수 실시간',
            '주요 업종 지수 현황',
            '시장 등락 현황',
            '거래량/거래대금 추이',
            '프로그램 매매 동향'
          ]
        },
        {
          title: '✅ 포트폴리오 현황',
          details: [
            '보유 종목 실시간 시세',
            '평가 손익 실시간 계산',
            '포트폴리오 수익률 차트',
            '종목별 비중 파이차트',
            '일별 손익 추이'
          ]
        },
        {
          title: '⏳ 실시간 시세 WebSocket',
          details: [
            'WebSocket 연결 관리',
            '실시간 호가 수신',
            '체결 데이터 스트리밍',
            '1초 단위 가격 업데이트',
            '연결 재시도 로직'
          ]
        },
        {
          title: '⏳ 실시간 차트',
          details: [
            '분봉/일봉 실시간 업데이트',
            'TradingView 차트 통합',
            '기술적 지표 오버레이',
            '거래량 프로파일',
            '주문 흐름 시각화'
          ]
        },
        {
          title: '⏳ 주문 패널',
          details: [
            '원클릭 주문 시스템',
            '예약 주문 설정',
            '주문 체결 알림',
            '미체결 주문 관리',
            '주문 히스토리'
          ]
        }
      ]
    },
    {
      id: 9,
      title: '자동매매 시스템',
      status: 'in-progress',
      priority: 'high',
      icon: <TrendingUp />,
      period: '2024.08.31 - 진행중',
      description: '키움 OpenAPI 연동 자동매매 시스템 구축',
      subtasks: [
        {
          title: '✅ 자동매매 UI',
          details: [
            '전략 선택 인터페이스',
            '자동매매 ON/OFF 토글',
            '실행 중인 전략 모니터링',
            '매매 로그 실시간 표시',
            '수익률 실시간 추적'
          ]
        },
        {
          title: '✅ 전략 실행 컨트롤',
          details: [
            '전략 시작/중지/일시정지',
            '긴급 정지 버튼',
            '전략별 자금 할당',
            '동시 실행 전략 관리',
            '전략 우선순위 설정'
          ]
        },
        {
          title: '⏳ 키움 API 서버',
          details: [
            'Python FastAPI 서버 구축',
            '키움 OpenAPI 연동',
            'COM 객체 관리',
            '이벤트 핸들러 구현',
            'API 요청 큐잉 시스템'
          ]
        },
        {
          title: '⏳ 실시간 주문 실행',
          details: [
            '신호 발생 시 자동 주문',
            '주문 체결 확인',
            '부분 체결 처리',
            '주문 실패 재시도',
            '슬리피지 관리'
          ]
        },
        {
          title: '⏳ 포지션 모니터링',
          details: [
            '실시간 포지션 추적',
            '손익 실시간 계산',
            '리스크 지표 모니터링',
            '포지션 조정 자동화',
            '일일 정산 리포트'
          ]
        }
      ]
    },
    {
      id: 10,
      title: '실시간 신호 모니터링',
      status: 'pending',
      priority: 'medium',
      icon: <AutoGraph />,
      period: '2024.09 예정',
      description: '매매 신호 실시간 감지 및 알림 시스템',
      subtasks: [
        {
          title: '매매 신호 감지',
          details: [
            '전략별 신호 모니터링',
            '복합 조건 신호 감지',
            '신호 강도 계산',
            '신호 유효성 검증',
            '오류 신호 필터링'
          ]
        },
        {
          title: '신호 알림 시스템',
          details: [
            '실시간 푸시 알림',
            '이메일 알림',
            '카카오톡 알림',
            'SMS 알림 (긴급)',
            '알림 우선순위 관리'
          ]
        },
        {
          title: '신호 히스토리',
          details: [
            '과거 신호 기록',
            '신호 성공률 분석',
            '신호별 수익률 추적',
            '패턴 분석',
            '신호 백테스팅'
          ]
        },
        {
          title: '신호 필터링',
          details: [
            '노이즈 필터링',
            '중복 신호 제거',
            '신호 검증 로직',
            '시장 상황 필터',
            'VIP 신호 우선순위'
          ]
        },
        {
          title: '신호 대시보드',
          details: [
            '실시간 신호 목록',
            '신호 차트 시각화',
            '신호 통계 분석',
            '종목별 신호 분포',
            '시간대별 신호 분석'
          ]
        }
      ]
    },
    {
      id: 11,
      title: '성과 분석 대시보드',
      status: 'pending',
      priority: 'medium',
      icon: <Assessment />,
      period: '2024.09 예정',
      description: '투자 성과 종합 분석 및 리포팅 시스템',
      subtasks: [
        {
          title: '수익률 분석',
          details: [
            '일/주/월/년 수익률',
            'CAGR 계산',
            '시간 가중 수익률',
            '금액 가중 수익률',
            '위험 조정 수익률'
          ]
        },
        {
          title: '포트폴리오 분석',
          details: [
            '자산 배분 분석',
            '섹터 배분 분석',
            '집중도 분석',
            '상관관계 분석',
            '효율적 프론티어'
          ]
        },
        {
          title: '벤치마크 비교',
          details: [
            'KOSPI/KOSDAQ 대비',
            '업종 지수 대비',
            '알파/베타 계산',
            '추적 오차 분석',
            '정보 비율 계산'
          ]
        },
        {
          title: '리스크 모니터링',
          details: [
            'VaR 실시간 계산',
            'CVaR 분석',
            '스트레스 테스트',
            '시나리오 분석',
            '리스크 기여도 분석'
          ]
        },
        {
          title: '리포트 생성',
          details: [
            '일일 리포트 자동 생성',
            '월간 성과 리포트',
            'PDF 내보내기',
            'Excel 데이터 추출',
            '맞춤형 리포트 템플릿'
          ]
        }
      ]
    },
    {
      id: 12,
      title: 'AI 포트폴리오 최적화',
      status: 'pending',
      priority: 'medium',
      icon: <AutoGraph />,
      period: '2024.10 예정',
      description: '머신러닝 기반 포트폴리오 최적화 시스템',
      subtasks: [
        {
          title: 'ML 모델 개발',
          details: [
            'LSTM 가격 예측 모델',
            'Random Forest 종목 선택',
            'XGBoost 타이밍 모델',
            '강화학습 매매 에이전트',
            '앙상블 모델 구축'
          ]
        },
        {
          title: '포트폴리오 최적화',
          details: [
            'Mean-Variance 최적화',
            'Black-Litterman 모델',
            'Risk Parity 전략',
            'Maximum Sharpe 최적화',
            'Minimum Variance 포트폴리오'
          ]
        },
        {
          title: '리밸런싱 자동화',
          details: [
            '주기적 리밸런싱',
            '임계값 기반 리밸런싱',
            '동적 리밸런싱',
            '세금 최적화 리밸런싱',
            '거래 비용 최소화'
          ]
        },
        {
          title: 'AI 추천 시스템',
          details: [
            '종목 추천 엔진',
            '매매 타이밍 추천',
            '포트폴리오 구성 추천',
            '리스크 수준 추천',
            '전략 조합 추천'
          ]
        },
        {
          title: '백테스팅 및 검증',
          details: [
            'Walk-forward 분석',
            'Out-of-sample 테스트',
            '교차 검증',
            '과적합 방지',
            '실시간 성과 추적'
          ]
        }
      ]
    },
    {
      id: 13,
      title: '알림 시스템',
      status: 'pending',
      priority: 'medium',
      icon: <Notifications />,
      period: '2024.10 예정',
      description: '다채널 알림 및 커뮤니케이션 시스템',
      subtasks: [
        {
          title: '이메일 알림',
          details: [
            'SendGrid API 연동',
            '템플릿 기반 이메일',
            '일일 요약 이메일',
            '거래 확인 이메일',
            '리포트 첨부 이메일'
          ]
        },
        {
          title: '텔레그램 봇',
          details: [
            'Telegram Bot API 연동',
            '실시간 알림 전송',
            '명령어 기반 조회',
            '차트 이미지 전송',
            '그룹 채널 지원'
          ]
        },
        {
          title: '푸시 알림',
          details: [
            'FCM 연동',
            'iOS/Android 푸시',
            'Web Push API',
            '알림 그룹화',
            '알림 액션 버튼'
          ]
        },
        {
          title: '알림 설정',
          details: [
            '알림 유형별 ON/OFF',
            '알림 시간대 설정',
            '알림 빈도 제한',
            '중요도 설정',
            'Do Not Disturb 모드'
          ]
        },
        {
          title: '알림 관리',
          details: [
            '알림 히스토리',
            '읽음/안읽음 관리',
            '알림 검색',
            '벌크 알림 관리',
            '알림 분석 대시보드'
          ]
        }
      ]
    },
    {
      id: 14,
      title: '모바일 반응형 UI',
      status: 'pending',
      priority: 'low',
      icon: <Dashboard />,
      period: '2024.11 예정',
      description: '모바일 최적화 및 PWA 구현',
      subtasks: [
        {
          title: '반응형 레이아웃',
          details: [
            '모바일 브레이크포인트 설정',
            '플렉스박스/그리드 재구성',
            '터치 친화적 UI 요소',
            '스와이프 제스처',
            '하단 네비게이션 바'
          ]
        },
        {
          title: '모바일 최적화',
          details: [
            '이미지 레이지 로딩',
            '코드 스플리팅',
            '번들 크기 최적화',
            '캐싱 전략',
            '오프라인 지원'
          ]
        },
        {
          title: 'PWA 구현',
          details: [
            'Service Worker 등록',
            'Manifest 파일 생성',
            '앱 아이콘 설정',
            '스플래시 스크린',
            '홈 화면 추가 프롬프트'
          ]
        },
        {
          title: '모바일 전용 기능',
          details: [
            '생체 인증 로그인',
            '퀵 액션 메뉴',
            '위젯 지원',
            '다크 모드 자동 전환',
            '배터리 절약 모드'
          ]
        },
        {
          title: '성능 최적화',
          details: [
            'Virtual scrolling',
            'Debounce/Throttle',
            'React.memo 최적화',
            'useMemo/useCallback',
            'Web Workers 활용'
          ]
        }
      ]
    },
    {
      id: 15,
      title: '테스트 및 최적화',
      status: 'pending',
      priority: 'low',
      icon: <BugReport />,
      period: '2024.11 예정',
      description: '품질 보증 및 성능 최적화',
      subtasks: [
        {
          title: '단위 테스트',
          details: [
            'Jest 테스트 환경 구성',
            'React Testing Library',
            '컴포넌트 단위 테스트',
            '커스텀 훅 테스트',
            '유틸리티 함수 테스트'
          ]
        },
        {
          title: '통합 테스트',
          details: [
            'E2E 테스트 (Cypress)',
            'API 통합 테스트',
            '시나리오 테스트',
            '크로스 브라우저 테스트',
            '모바일 디바이스 테스트'
          ]
        },
        {
          title: '성능 최적화',
          details: [
            'Lighthouse 성능 분석',
            'Bundle 크기 최적화',
            'Tree shaking',
            'CDN 최적화',
            'Database 쿼리 최적화'
          ]
        },
        {
          title: '보안 점검',
          details: [
            'OWASP Top 10 점검',
            'SQL Injection 방지',
            'XSS 방지',
            'CSRF 토큰',
            'API Rate Limiting'
          ]
        },
        {
          title: '접근성 개선',
          details: [
            'WCAG 2.1 준수',
            '키보드 네비게이션',
            '스크린 리더 지원',
            'Color contrast 검증',
            'ARIA labels 추가'
          ]
        }
      ]
    },
    {
      id: 16,
      title: '문서화 및 배포',
      status: 'pending',
      priority: 'low',
      icon: <Description />,
      period: '2024.12 예정',
      description: '프로젝트 문서화 및 프로덕션 배포',
      subtasks: [
        {
          title: 'API 문서화',
          details: [
            'OpenAPI 3.0 스펙 작성',
            'Swagger UI 통합',
            'API 예제 코드',
            'Rate limit 문서화',
            'WebSocket API 문서'
          ]
        },
        {
          title: '사용자 가이드',
          details: [
            '온보딩 튜토리얼',
            '기능별 사용 설명서',
            '비디오 가이드 제작',
            'FAQ 섹션',
            '트러블슈팅 가이드'
          ]
        },
        {
          title: '개발자 문서',
          details: [
            '아키텍처 문서',
            '컴포넌트 문서 (Storybook)',
            '코드 컨벤션 가이드',
            'Git 브랜치 전략',
            'CI/CD 파이프라인 문서'
          ]
        },
        {
          title: 'Vercel 배포',
          details: [
            'Vercel 프로젝트 설정',
            '환경 변수 설정',
            'Custom domain 연결',
            'Preview deployments',
            'Production 배포'
          ]
        },
        {
          title: '모니터링 설정',
          details: [
            'Sentry 에러 트래킹',
            'Google Analytics',
            'Performance monitoring',
            'Uptime monitoring',
            'Log aggregation'
          ]
        }
      ]
    }
  ]

  const completedTasks = tasks.filter(t => t.status === 'done').length
  const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length
  const totalTasks = tasks.length
  const progress = (completedTasks / totalTasks) * 100

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'done': return <CheckCircle color="success" />
      case 'in-progress': return <Schedule color="warning" />
      default: return <Schedule color="disabled" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch(priority) {
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'default'
    }
  }

  const activeStep = tasks.findIndex(task => task.status === 'in-progress')

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          maxHeight: '95vh',
          height: '95vh'
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h5">
            🚀 KyyQuant AI Solution 개발 로드맵
          </Typography>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        {/* 전체 진행률 */}
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h6" fontWeight="bold">전체 프로젝트 진행률</Typography>
            <Typography variant="h4" color="primary" fontWeight="bold">
              {progress.toFixed(1)}%
            </Typography>
          </Stack>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 12, borderRadius: 6 }}
          />
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            <Chip label={`총 ${totalTasks}개 작업`} size="medium" />
            <Chip label={`완료: ${completedTasks}개`} color="success" size="medium" />
            <Chip label={`진행중: ${inProgressTasks}개`} color="warning" size="medium" />
            <Chip label={`대기: ${totalTasks - completedTasks - inProgressTasks}개`} size="medium" />
          </Stack>
        </Paper>

        {/* 현재 진행 상황 알림 */}
        {tasks.filter(t => t.status === 'in-progress').length > 0 && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              💡 현재 진행 중인 작업
            </Typography>
            <Stack spacing={1} sx={{ mt: 1 }}>
              {tasks.filter(t => t.status === 'in-progress').map(task => (
                <Box key={task.id}>
                  <Typography variant="body1" fontWeight="500">
                    • Task #{task.id}: {task.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                    {task.description}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Alert>
        )}

        {/* 작업 목록 */}
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          📊 상세 개발 일정
        </Typography>
        
        {tasks.map((task, index) => (
          <Accordion key={task.id} defaultExpanded={task.status === 'in-progress'}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getStatusIcon(task.status)}
                  {task.icon}
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="subtitle1" fontWeight="bold">
                      #{task.id} {task.title}
                    </Typography>
                    <Chip 
                      label={task.priority === 'high' ? '높음' : 
                             task.priority === 'medium' ? '중간' : '낮음'} 
                      size="small" 
                      color={getPriorityColor(task.priority) as any}
                    />
                    {task.status === 'done' && (
                      <Chip label="완료" size="small" color="success" />
                    )}
                    {task.status === 'in-progress' && (
                      <Chip label="진행중" size="small" color="warning" />
                    )}
                    {task.status === 'pending' && (
                      <Chip label="대기" size="small" />
                    )}
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {task.period} | {task.description}
                  </Typography>
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={3}>
                {task.subtasks.map((subtask, idx) => (
                  <Box key={idx}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      {subtask.title}
                    </Typography>
                    {'details' in subtask && (
                      <List dense sx={{ ml: 2 }}>
                        {subtask.details.map((detail, didx) => (
                          <ListItem key={didx} sx={{ py: 0.5 }}>
                            <ListItemText 
                              primary={`• ${detail}`}
                              primaryTypographyProps={{ 
                                variant: 'body2',
                                color: task.status === 'done' ? 'text.secondary' : 'text.primary'
                              }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </Box>
                ))}
              </Stack>
            </AccordionDetails>
          </Accordion>
        ))}

        <Divider sx={{ my: 4 }} />

        {/* 기술 스택 */}
        <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
          <Typography variant="h6" gutterBottom>
            🛠️ 기술 스택
          </Typography>
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom>
                Frontend
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="React 18.2" size="small" />
                <Chip label="TypeScript 5.0" size="small" />
                <Chip label="Vite 4.5" size="small" />
                <Chip label="Material-UI v5.14" size="small" />
                <Chip label="Redux Toolkit 1.9" size="small" />
                <Chip label="React Router v6" size="small" />
                <Chip label="Chart.js 4.4" size="small" />
                <Chip label="Axios" size="small" />
                <Chip label="date-fns" size="small" />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" color="success.main" gutterBottom>
                Backend & Database
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Supabase" size="small" color="success" />
                <Chip label="PostgreSQL 15" size="small" color="success" />
                <Chip label="Supabase Auth" size="small" color="success" />
                <Chip label="Supabase Realtime" size="small" color="success" />
                <Chip label="Row Level Security" size="small" color="success" />
                <Chip label="PostgREST" size="small" color="success" />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" color="warning.main" gutterBottom>
                Trading System (개발 예정)
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Python 3.11" size="small" color="warning" />
                <Chip label="FastAPI" size="small" color="warning" />
                <Chip label="키움 OpenAPI" size="small" color="warning" />
                <Chip label="WebSocket" size="small" color="warning" />
                <Chip label="Redis" size="small" color="warning" />
                <Chip label="Celery" size="small" color="warning" />
              </Stack>
            </Box>

            <Box>
              <Typography variant="subtitle1" fontWeight="bold" color="info.main" gutterBottom>
                DevOps & Tools
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Vercel" size="small" color="info" />
                <Chip label="GitHub Actions" size="small" color="info" />
                <Chip label="Docker" size="small" color="info" />
                <Chip label="Sentry" size="small" color="info" />
                <Chip label="Google Analytics" size="small" color="info" />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} variant="contained" size="large">
          닫기
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default RoadmapDialog