
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
    Paper,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
    IconButton,
    Alert
} from '@mui/material'
import {
    Close,
    Assignment,
    Storage,
    Security,
    Code,
    TrendingUp,
    CreditCard,
    CloudQueue,
    Group,
    NotificationsActive,
    Timeline
} from '@mui/icons-material'

interface RoadmapDialogV2Props {
    open: boolean
    onClose: () => void
}

const RoadmapDialogV2: React.FC<RoadmapDialogV2Props> = ({ open, onClose }) => {
    const tasks = [
        {
            id: 1,
            title: '멀티유저(SaaS) 아키텍처 기반 구축',
            status: 'in-progress',
            priority: 'high',
            icon: <CloudQueue />,
            period: 'Phase 2-1 (현재)',
            description: '단일 사용자 시스템을 다중 사용자 지원 가능한 SaaS 구조로 전환',
            subtasks: [
                {
                    title: '🔄 데이터베이스 스키마 확장',
                    details: [
                        'Strategy Universe 연결 테이블 생성',
                        'Subscription(구독) 로직을 Strategy Clone(복제) 모델로 전환',
                        '사용자별 자금 할당(Allocated Capital) 컬럼 추가',
                        'Row Level Security (RLS) 정책 강화'
                    ]
                },
                {
                    title: '🔄 사용자 인증/권한 고도화',
                    details: [
                        '사용자별 API Key 암호화 저장 관리',
                        'Role 기반 접근 제어 (Admin vs User)',
                        '세션 관리 및 보안 강화'
                    ]
                }
            ]
        },
        {
            id: 2,
            title: '나의 전략 구독 시스템',
            status: 'pending',
            priority: 'high',
            icon: <Assignment />,
            period: 'Phase 2-2',
            description: '사용자가 마켓의 전략을 가져와 자신만의 유니버스로 설정하는 기능',
            subtasks: [
                {
                    title: '전략 설정(Config) UI 개발',
                    details: [
                        '[나의 전략] 설정 팝업 구현',
                        '투자 유니버스(종목 필터) 연결 기능',
                        '전략별 운용 자금(예: 100만원) 설정 기능',
                        '전략 활성화/비활성화 스위치'
                    ]
                },
                {
                    title: '전략 마켓 연동',
                    details: [
                        'Market 전략 "Get" 시 사용자 전략으로 복제',
                        '기본 설정값(파라미터) 유지하되 수정 가능하도록 구현'
                    ]
                }
            ]
        },
        {
            id: 3,
            title: '멀티 테넌트 주문 실행 엔진',
            status: 'pending',
            priority: 'critical',
            icon: <TrendingUp />,
            period: 'Phase 2-3',
            description: '중앙 서버에서 다수 사용자의 API로 주문을 병렬 실행하는 엔진',
            subtasks: [
                {
                    title: '중앙 주문 집행기(Central Executor)',
                    details: [
                        'Asyncio 기반 비동기 주문 처리',
                        '사용자별 Kiwoom API 토큰 독립 관리',
                        '주문 큐(Queue) 및 속도 제한(Rate Limiting) 관리',
                        '실행 로그의 사용자별 격리 저장'
                    ]
                },
                {
                    title: '시스템 안정성 확보',
                    details: [
                        '주문 실패 시 재시도(Retry) 로직',
                        '사용자별 예수금/보유종목 실시간 동기화',
                        '긴급 전체 청산(Panic Button) 기능 고도화'
                    ]
                }
            ]
        },
        {
            id: 4,
            title: '결제 및 구독 멤버십 시스템',
            status: 'pending',
            priority: 'high',
            icon: <CreditCard />,
            period: 'Phase 2-4',
            description: '서비스 수익화를 위한 결제 모듈 연동 및 멤버십 관리',
            subtasks: [
                {
                    title: 'PG사 연동 (PortOne/Iamport)',
                    details: [
                        '카드 결제 및 간편 결제(카카오페이 등) 연동',
                        '결제 검증 및 승인 프로세스 구현',
                        '결제 취소 및 환불 로직'
                    ]
                },
                {
                    title: '멤버십 관리',
                    details: [
                        '멤버십 플랜 설계 (Free, Basic, Pro)',
                        '구독 기간 관리 및 자동 갱신 처리',
                        '멤버십 등급별 기능 제한(전략 수, 자금 한도 등) 적용',
                        '결제 이력 및 인보이스 생성'
                    ]
                }
            ]
        },
        {
            id: 5,
            title: '사용자 대시보드 및 알림',
            status: 'pending',
            priority: 'medium',
            icon: <NotificationsActive />,
            period: 'Phase 2-5',
            description: '개별 사용자를 위한 모니터링 환경 구축',
            subtasks: [
                {
                    title: '개인화 대시보드',
                    details: [
                        '나의 자산 추이 그래프',
                        '활성 전략별 실시간 수익률',
                        'Trading History (매매 일지) 자동 생성'
                    ]
                },
                {
                    title: '실시간 알림 서비스',
                    details: [
                        '매매 체결 시 텔레그램/카카오톡 알림',
                        '에러 발생 또는 자금 부족 알림',
                        '일간 수익률 리포트 발송'
                    ]
                }
            ]
        },
        {
            id: 6,
            title: '시스템 안정성 및 마켓 데이터 고도화',
            status: 'done',
            priority: 'medium',
            icon: <Security />,
            period: 'Phase 2-6 (완료)',
            description: '글로벌 시장 데이터 정합성 확보 및 시스템 예외처리 강화',
            subtasks: [
                {
                    title: '✅ 마켓 데이터 안정화 (Smart Merge)',
                    details: [
                        'NAS 데이터 수집 이중화 (Primary/Backup)',
                        'Partial Update 시 캐시 보존 로직(Smart Merge) 적용',
                        '스켈레톤 UI 발생 원인(Partial Failure) 차단'
                    ]
                },
                {
                    title: '✅ AWS 백엔드/NAS 동기화',
                    details: [
                        'Docker 컨테이너 Hot-Patching 적용',
                        '서버 간 데이터 파이프라인(Push Model) 최적화'
                    ]
                }
            ]
        }
    ]

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    minHeight: '80vh',
                    maxHeight: '90vh'
                }
            }}
        >
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, borderBottom: 1, borderColor: 'divider' }}>
                <Timeline color="secondary" />
                <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                        Phase 2: Multi-User SaaS & Payment
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        확장성과 수익화를 위한 차세대 플랫폼 개발 로드맵
                    </Typography>
                </Box>
                <IconButton onClick={onClose}>
                    <Close />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ p: 0 }}>
                <Box sx={{ display: 'flex', height: '100%' }}>
                    {/* Left Side: Steps */}
                    <Box sx={{ width: '100%', p: 3 }}>
                        <Stepper orientation="vertical">
                            {tasks.map((task) => (
                                <Step key={task.id} active={true} expanded={true}>
                                    <StepLabel
                                        StepIconComponent={() => (
                                            <Box sx={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                width: 40,
                                                height: 40,
                                                borderRadius: '50%',
                                                bgcolor: task.status === 'done' ? 'success.main' :
                                                    task.status === 'in-progress' ? 'secondary.main' : 'action.disabledBackground',
                                                color: 'white'
                                            }}>
                                                {task.icon}
                                            </Box>
                                        )}
                                    >
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="h6" sx={{
                                                fontWeight: 'bold',
                                                color: task.status === 'done' ? 'text.primary' :
                                                    task.status === 'in-progress' ? 'secondary.main' : 'text.secondary'
                                            }}>
                                                {task.title}
                                            </Typography>
                                            <Chip
                                                label={task.status === 'done' ? '완료' : task.status === 'in-progress' ? '진행중' : '대기'}
                                                size="small"
                                                color={task.status === 'done' ? 'success' : task.status === 'in-progress' ? 'secondary' : 'default'}
                                                variant={task.status === 'pending' ? 'outlined' : 'filled'}
                                            />
                                            <Chip
                                                label={task.period}
                                                size="small"
                                                variant="outlined"
                                                sx={{ ml: 'auto' }}
                                            />
                                        </Box>
                                    </StepLabel>
                                    <StepContent>
                                        <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default', mt: 1, mb: 2 }}>
                                            <Typography variant="body2" color="text.secondary" paragraph>
                                                {task.description}
                                            </Typography>
                                            <List dense disablePadding>
                                                {task.subtasks.map((sub, idx) => (
                                                    <React.Fragment key={idx}>
                                                        <ListItem>
                                                            <ListItemIcon sx={{ minWidth: 32 }}>
                                                                {sub.title.startsWith('✅') ? (
                                                                    <Assignment color="success" fontSize="small" />
                                                                ) : (
                                                                    <Code color="action" fontSize="small" />
                                                                )}
                                                            </ListItemIcon>
                                                            <ListItemText
                                                                primary={sub.title}
                                                                secondary={
                                                                    <Stack direction="row" spacing={1} sx={{ mt: 0.5, flexWrap: 'wrap', gap: 0.5 }}>
                                                                        {sub.details.map((detail, dIdx) => (
                                                                            <Chip
                                                                                key={dIdx}
                                                                                label={detail}
                                                                                size="small"
                                                                                variant="outlined"
                                                                                sx={{ fontSize: '0.75rem' }}
                                                                            />
                                                                        ))}
                                                                    </Stack>
                                                                }
                                                            />
                                                        </ListItem>
                                                        {idx < task.subtasks.length - 1 && <Divider component="li" variant="inset" />}
                                                    </React.Fragment>
                                                ))}
                                            </List>
                                        </Paper>
                                    </StepContent>
                                </Step>
                            ))}
                        </Stepper>
                    </Box>
                </Box>
            </DialogContent>

            <DialogActions sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                <Button onClick={onClose} variant="contained" color="primary">
                    확인
                </Button>
            </DialogActions>
        </Dialog>
    )
}

export default RoadmapDialogV2
