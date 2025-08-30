import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Stack,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material'
import {
  ExpandMore,
  CheckCircle,
  Schedule,
  Assignment,
  TrendingUp,
  Storage,
  Security,
  Dashboard,
  Code,
  Assessment,
  AutoGraph,
  Notifications,
  BugReport,
  Description,
  Settings
} from '@mui/icons-material'

const Notice: React.FC = () => {
  const tasks = [
    {
      id: 1,
      title: 'KyyQuant AI Solution 프로젝트 초기 설정',
      status: 'done',
      priority: 'high',
      icon: <Assignment />,
      description: 'React, Vite, TypeScript 환경 구성 및 기본 프로젝트 구조 설정',
      subtasks: [
        '✅ React + Vite 프로젝트 초기화',
        '✅ TypeScript 설정',
        '✅ Material-UI 테마 설정',
        '✅ Redux Toolkit 상태관리 구성',
        '✅ 라우팅 시스템 구축'
      ]
    },
    {
      id: 2,
      title: '데이터베이스 스키마 설계',
      status: 'done',
      priority: 'high',
      icon: <Storage />,
      dependencies: [1],
      subtasks: [
        '✅ 사용자 프로필 테이블 (profiles)',
        '✅ 전략 테이블 (strategies)',
        '✅ 백테스팅 결과 테이블 (backtest_results)',
        '✅ 백테스팅 상세 테이블 (trades, daily_returns, monthly_returns)',
        '✅ 섹터 성과 테이블 (sector_performance)',
        '✅ 리스크 지표 테이블 (risk_metrics)',
        '✅ 투자 설정 테이블 (investment_settings)'
      ]
    },
    {
      id: 3,
      title: 'Supabase 인증 시스템',
      status: 'done',
      priority: 'high',
      icon: <Security />,
      dependencies: [2],
      subtasks: [
        '✅ Supabase Auth 연동',
        '✅ 로그인/회원가입 UI 구현',
        '✅ 소셜 로그인 (Google, GitHub)',
        '✅ 세션 관리 및 자동 로그인',
        '✅ 프로필 관리 시스템',
        '✅ 관리자 권한 시스템'
      ]
    },
    {
      id: 4,
      title: '전략 빌더 시스템',
      status: 'done',
      priority: 'high',
      icon: <Code />,
      dependencies: [3],
      subtasks: [
        '✅ 보조지표 선택 UI (RSI, MACD, BB, MA, 일목균형표 등)',
        '✅ 조건 설정 인터페이스 (AND/OR 로직)',
        '✅ 일목균형표 특수 조건 구현',
        '✅ 리스크 관리 슬라이더 UI',
        '✅ 전략 저장/불러오기 기능',
        '✅ 코드 생성기',
        '✅ 퀵 백테스트 기능'
      ]
    },
    {
      id: 5,
      title: '백테스팅 시스템',
      status: 'done',
      priority: 'high',
      icon: <Assessment />,
      dependencies: [4],
      subtasks: [
        '✅ Supabase 백테스팅 데이터 연동',
        '✅ 수익률 곡선 차트 (Chart.js)',
        '✅ 리스크 분석 (샤프지수, 최대낙폭 등)',
        '✅ 거래 분석 (승률, 손익비)',
        '✅ 섹터별 성과 분석',
        '✅ 월별 수익률 히트맵',
        '✅ 상세 거래 내역 테이블',
        '✅ 백테스팅 결과 저장/불러오기'
      ]
    },
    {
      id: 6,
      title: '투자 설정 시스템',
      status: 'done',
      priority: 'high',
      icon: <Settings />,
      dependencies: [5],
      subtasks: [
        '✅ 투자 유니버스 설정 (시가총액, PER, ROE 등)',
        '✅ 매매 조건 상세 설정',
        '✅ 업종지표 설정 (섹터 상대강도)',
        '✅ 포트폴리오 관리 설정',
        '✅ 분할매매 전략 설정',
        '✅ 위험관리 시스템 (시스템 CUT)',
        '✅ 설정 저장/불러오기'
      ]
    },
    {
      id: 7,
      title: '실시간 대시보드 개발',
      status: 'in-progress',
      priority: 'high',
      icon: <Dashboard />,
      dependencies: [6],
      subtasks: [
        '✅ 시장 개요 위젯',
        '✅ 포트폴리오 현황',
        '⏳ 실시간 시세 WebSocket 연동',
        '⏳ 실시간 차트 업데이트',
        '⏳ 주문 패널 구현'
      ]
    },
    {
      id: 8,
      title: '자동매매 시스템',
      status: 'in-progress',
      priority: 'high',
      icon: <TrendingUp />,
      dependencies: [7],
      subtasks: [
        '✅ 자동매매 UI 패널',
        '✅ 전략 실행/중지 컨트롤',
        '⏳ 키움 API 연동 서버',
        '⏳ 실시간 주문 실행',
        '⏳ 포지션 모니터링'
      ]
    },
    {
      id: 9,
      title: '실시간 신호 모니터링',
      status: 'pending',
      priority: 'medium',
      icon: <AutoGraph />,
      dependencies: [8],
      subtasks: [
        '실시간 매수/매도 신호',
        '조건 충족 알림',
        '신호 히스토리',
        '신호 필터링'
      ]
    },
    {
      id: 10,
      title: '성과 분석 대시보드',
      status: 'pending',
      priority: 'medium',
      icon: <Assessment />,
      dependencies: [8],
      subtasks: [
        '일/주/월 수익률 차트',
        '포트폴리오 성과 분석',
        '벤치마크 대비 성과',
        '리스크 지표 모니터링'
      ]
    },
    {
      id: 11,
      title: 'AI 포트폴리오 최적화',
      status: 'pending',
      priority: 'medium',
      icon: <AutoGraph />,
      dependencies: [10],
      subtasks: [
        'ML 모델 통합',
        '포트폴리오 최적화 알고리즘',
        '리밸런싱 자동화',
        'AI 추천 시스템'
      ]
    },
    {
      id: 12,
      title: '알림 시스템',
      status: 'pending',
      priority: 'medium',
      icon: <Notifications />,
      dependencies: [9],
      subtasks: [
        '이메일 알림',
        '텔레그램 봇 연동',
        '푸시 알림',
        '알림 설정 관리'
      ]
    },
    {
      id: 13,
      title: '모바일 반응형 UI',
      status: 'pending',
      priority: 'low',
      icon: <Dashboard />,
      dependencies: [10],
      subtasks: [
        '모바일 레이아웃 최적화',
        '터치 인터페이스',
        'PWA 구현',
        '모바일 전용 기능'
      ]
    },
    {
      id: 14,
      title: '테스트 및 최적화',
      status: 'pending',
      priority: 'low',
      icon: <BugReport />,
      dependencies: [12],
      subtasks: [
        '단위 테스트',
        '통합 테스트',
        '성능 최적화',
        '보안 점검'
      ]
    },
    {
      id: 15,
      title: '문서화 및 배포',
      status: 'pending',
      priority: 'low',
      icon: <Description />,
      dependencies: [14],
      subtasks: [
        'API 문서화',
        '사용자 가이드',
        'Vercel 프로덕션 배포',
        '모니터링 설정'
      ]
    }
  ]

  const completedTasks = tasks.filter(t => t.status === 'done').length
  const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length
  const totalTasks = tasks.length
  const progress = (completedTasks / totalTasks) * 100

  const getPriorityColor = (priority: string) => {
    switch(priority) {
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'done': return <CheckCircle color="success" />
      case 'in-progress': return <Schedule color="warning" />
      default: return <Schedule color="disabled" />
    }
  }

  return (
    <Box>
      <Stack spacing={3}>
        {/* 프로젝트 개요 */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            🚀 KyyQuant AI Solution 개발 계획
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            AI 기반 자동매매 플랫폼 구축 프로젝트
          </Typography>
          
          <Box sx={{ mt: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2">전체 진행률</Typography>
              <Typography variant="body2">{progress.toFixed(0)}%</Typography>
            </Stack>
            <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
          </Box>

          <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
            <Chip label={`총 ${totalTasks}개 작업`} size="small" />
            <Chip label={`완료: ${completedTasks}`} color="success" size="small" />
            <Chip label={`진행중: ${inProgressTasks}`} color="warning" size="small" />
            <Chip label={`대기: ${totalTasks - completedTasks - inProgressTasks}`} size="small" />
          </Stack>
        </Paper>

        {/* 주요 공지사항 */}
        <Alert severity="success">
          <Typography variant="subtitle2" gutterBottom>
            ✨ 최근 완료된 기능
          </Typography>
          <Stack spacing={1} sx={{ mt: 1 }}>
            <Typography variant="body2">
              • Supabase 인증 시스템 완성 (소셜 로그인, 프로필 관리)
            </Typography>
            <Typography variant="body2">
              • 전략 빌더 고도화 (일목균형표, 리스크 관리 슬라이더)
            </Typography>
            <Typography variant="body2">
              • 백테스팅 시스템 Supabase 연동 완료
            </Typography>
            <Typography variant="body2">
              • 투자 설정 시스템 구현 (업종지표, 분할매매, 시스템 CUT)
            </Typography>
          </Stack>
        </Alert>
        
        <Alert severity="info">
          <Typography variant="subtitle2" gutterBottom>
            💡 현재 진행 중인 작업
          </Typography>
          <Stack spacing={1} sx={{ mt: 1 }}>
            <Typography variant="body2">
              • Task #7: 실시간 대시보드 - WebSocket 연동 및 실시간 차트
            </Typography>
            <Typography variant="body2">
              • Task #8: 자동매매 시스템 - 키움 API 서버 연동
            </Typography>
          </Stack>
        </Alert>

        {/* 개발 로드맵 */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            📋 개발 로드맵
          </Typography>
          
          {tasks.map((task) => (
            <Accordion key={task.id} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
                  {task.icon}
                  <Box sx={{ flexGrow: 1 }}>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Typography variant="subtitle2">
                        #{task.id} {task.title}
                      </Typography>
                      <Chip 
                        label={task.priority} 
                        size="small" 
                        color={getPriorityColor(task.priority) as any}
                      />
                      {getStatusIcon(task.status)}
                    </Stack>
                  </Box>
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  {task.description && (
                    <Typography variant="body2" color="text.secondary">
                      {task.description}
                    </Typography>
                  )}
                  
                  {task.dependencies && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        의존성: Task #{task.dependencies.join(', #')}
                      </Typography>
                    </Box>
                  )}
                  
                  {task.subtasks && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        세부 작업:
                      </Typography>
                      <List dense>
                        {task.subtasks.map((subtask, index) => (
                          <ListItem key={index}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <Schedule fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={subtask}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Stack>
              </AccordionDetails>
            </Accordion>
          ))}
        </Paper>

        {/* 기술 스택 */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            🛠️ 기술 스택
          </Typography>
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Frontend
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="React 18" variant="outlined" color="primary" />
                <Chip label="TypeScript" variant="outlined" color="primary" />
                <Chip label="Vite" variant="outlined" color="primary" />
                <Chip label="Material-UI v5" variant="outlined" color="primary" />
                <Chip label="Redux Toolkit" variant="outlined" color="primary" />
                <Chip label="Chart.js" variant="outlined" color="primary" />
                <Chip label="React Router v6" variant="outlined" color="primary" />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Backend & Database
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Supabase" variant="outlined" color="success" />
                <Chip label="PostgreSQL" variant="outlined" color="success" />
                <Chip label="Supabase Auth" variant="outlined" color="success" />
                <Chip label="Supabase Realtime" variant="outlined" color="success" />
                <Chip label="Row Level Security" variant="outlined" color="success" />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Trading System (개발 예정)
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Python" variant="outlined" />
                <Chip label="FastAPI" variant="outlined" />
                <Chip label="키움 OpenAPI" variant="outlined" />
                <Chip label="WebSocket" variant="outlined" />
                <Chip label="Redis" variant="outlined" />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                DevOps & Deployment
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip label="Vercel" variant="outlined" color="warning" />
                <Chip label="GitHub Actions" variant="outlined" color="warning" />
                <Chip label="Docker" variant="outlined" color="warning" />
              </Stack>
            </Box>
          </Stack>
        </Paper>
      </Stack>
    </Box>
  )
}

export default Notice