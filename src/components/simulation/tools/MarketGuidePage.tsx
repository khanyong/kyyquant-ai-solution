import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Divider, Slider, Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton } from '@mui/material';
import { TrendingUp, AccountBalance, Speed, AttachMoney, Security, Close, House } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    primary: '#00D1FF',
    secondary: '#7F5AF0',
    success: '#2CB67D',
    warning: '#FFBB28',
    danger: '#EF4565',
    border: '#2A2F3A'
};

const RecommendationSection = () => {
    const [age, setAge] = React.useState<number>(35);
    const [goal, setGoal] = React.useState<string>('growth'); // growth, income, stability
    const [horizon, setHorizon] = React.useState<number>(10); // years
    const [risk, setRisk] = React.useState<number>(3); // 1-5

    const rec = React.useMemo(() => {
        let score = (80 - age) * 0.5 + Math.min(horizon, 20) * 1.5 + (risk * 12);
        if (goal === 'growth') score += 15;
        if (goal === 'income') score -= 5;
        if (goal === 'stability') score -= 25;

        let title = "";
        let desc = "";
        let portfolio = [];

        if (score >= 90) {
            title = "🚀 공격적 성장형 (Aggressive Growth)";
            desc = "변동성을 감내하더라도 자산 증식을 최우선으로 합니다.";
            portfolio = [
                { ticker: 'QQQ/TQQQ', name: '나스닥 기술주', weight: '50%', note: 'AI/반도체 주도 성장' },
                { ticker: 'SOXX', name: '반도체 ETF', weight: '30%', note: '핵심 산업 집중' },
                { ticker: 'SPY', name: 'S&P 500', weight: '20%', note: '기본 안전판' }
            ];
        } else if (score >= 60) {
            title = "📈 성장 추구형 (Growth Focus)";
            desc = "시장 수익률을 상회하는 성장을 추구합니다.";
            portfolio = [
                { ticker: 'SPY/VOO', name: 'S&P 500', weight: '40%', note: '시장 지수 추종' },
                { ticker: 'QQQ', name: '나스닥 100', weight: '30%', note: '성장 엔진' },
                { ticker: 'SCHD', name: '배당 성장', weight: '30%', note: '방어력 보강' }
            ];
        } else if (score >= 35) {
            title = "⚖️ 중립/배당형 (Balanced Income)";
            desc = "안정적인 현금 흐름과 적당한 성장을 동시에 추구합니다.";
            portfolio = [
                { ticker: 'SCHD', name: '배당 성장', weight: '40%', note: '배당+성장 밸런스' },
                { ticker: 'JEPI', name: '커버드콜', weight: '30%', note: '월 배당 현금 생활' },
                { ticker: 'SPY', name: 'S&P 500', weight: '30%', note: '인플레이션 헷지' }
            ];
        } else {
            title = "🛡️ 안정 추구형 (Conservative)";
            desc = "원금 보존과 은행 이자 이상의 수익을 목표로 합니다.";
            portfolio = [
                { ticker: 'SGOV', name: '단기 국채', weight: '50%', note: '파킹통장 대용 (안전)' },
                { ticker: 'JEPI', name: '커버드콜', weight: '30%', note: '고정 수입 확보' },
                { ticker: 'O', name: '리얼티인컴', weight: '20%', note: '부동산 월세' }
            ];
        }
        return { title, desc, portfolio };
    }, [age, goal, horizon, risk]);

    return (
        <Paper sx={{ p: 4, bgcolor: '#121212', border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
            <Grid container spacing={4}>
                {/* Inputs */}
                <Grid item xs={12} md={5}>
                    <Typography variant="h6" sx={{ mb: 3 }}>내 투자 성향 입력</Typography>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom>나이: {age}세</Typography>
                        <Slider value={age} onChange={(_, v) => setAge(v as number)} min={20} max={80} sx={{ color: THEME.primary }} />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom>투자 목적</Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            {['growth', 'income', 'stability'].map((g) => (
                                <Chip
                                    key={g}
                                    label={g === 'growth' ? '자산 증식' : g === 'income' ? '월 현금' : '원금 보존'}
                                    onClick={() => setGoal(g)}
                                    color={goal === g ? 'primary' : 'default'}
                                    variant={goal === g ? 'filled' : 'outlined'}
                                />
                            ))}
                        </Box>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom>투자 기간: {horizon}년 이상</Typography>
                        <Slider value={horizon} onChange={(_, v) => setHorizon(v as number)} min={1} max={30} sx={{ color: THEME.secondary }} />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                        <Typography gutterBottom>위험 감수 (1:보수적 ~ 5:적극적): {risk}</Typography>
                        <Slider value={risk} onChange={(_, v) => setRisk(v as number)} min={1} max={5} step={1} marks />
                    </Box>
                </Grid>

                {/* Vertical Divider */}
                <Grid item md={1} sx={{ display: { xs: 'none', md: 'flex' }, justifyContent: 'center' }}>
                    <Divider orientation="vertical" />
                </Grid>

                {/* Result */}
                <Grid item xs={12} md={6}>
                    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <Typography variant="overline" color={THEME.textDim} sx={{ mb: 1 }}>AI 분석 결과</Typography>
                        <Typography variant="h5" fontWeight="bold" sx={{ color: THEME.success, mb: 1 }}>
                            {rec.title}
                        </Typography>
                        <Typography variant="body2" color={THEME.textDim} sx={{ mb: 3 }}>
                            {rec.desc}
                        </Typography>

                        <Paper sx={{ bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>상품</TableCell>
                                        <TableCell align="right">비중</TableCell>
                                        <TableCell>이유</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {rec.portfolio.map((item, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell sx={{ fontWeight: 'bold', color: THEME.text }}>{item.ticker}</TableCell>
                                            <TableCell align="right" sx={{ color: THEME.primary }}>{item.weight}</TableCell>
                                            <TableCell sx={{ color: THEME.textDim, fontSize: '0.85rem' }}>{item.note}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </Paper>
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
};

const DetailedGuideDialog = ({ open, onClose }: { open: boolean, onClose: () => void }) => {
    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth PaperProps={{ sx: { bgcolor: '#1a1d26', color: '#E0E6ED', backgroundImage: 'none' } }}>
            <DialogTitle sx={{ borderBottom: '1px solid ' + THEME.border, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" fontWeight="bold">커버드 콜 (Covered Call) 완벽 가이드</Typography>
                <IconButton onClick={onClose} sx={{ color: THEME.textDim }}><Close /></IconButton>
            </DialogTitle>
            <DialogContent sx={{ p: 4 }}>
                {/* Step 1 */}
                <Box sx={{ mb: 5 }}>
                    <Typography variant="h5" fontWeight="bold" color={THEME.primary} sx={{ mb: 2 }}>1단계: 커버드 콜이 뭔가요?</Typography>
                    <Typography variant="h6" sx={{ mb: 2, fontStyle: 'italic', color: THEME.secondary }}>
                        "미래의 대박 수익을 포기하는 대신, 당장의 현금(보너스)을 챙기는 전략"
                    </Typography>

                    <Paper sx={{ p: 3, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2, mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <House sx={{ color: THEME.warning, fontSize: 40, mr: 2 }} />
                            <Typography variant="h6" fontWeight="bold">아파트 매매 계약 비유</Typography>
                        </Box>
                        <Typography paragraph>
                            여러분이 <b>10억 원짜리 아파트(주식)</b>를 가지고 있다고 상상해 보세요.
                        </Typography>
                        <Box sx={{ pl: 2, borderLeft: `4px solid ${THEME.warning}`, mb: 2 }}>
                            <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>어떤 사람이 솔깃한 제안을 합니다:</Typography>
                            <Typography variant="body1" fontWeight="bold">
                                "제가 지금 당장 <span style={{ color: THEME.success }}>1,000만 원(현금 보너스)</span>을 드릴게요.<br />
                                대신, 다음 달에 집값이 <b>11억 원 이상으로 폭등하면, 무조건 11억 원에 저한테 파셔야 해요.</b>"
                            </Typography>
                        </Box>
                        <Typography>여러분이 이 제안을 수락하는 것이 바로 <b>'커버드 콜'</b>입니다.</Typography>
                    </Paper>

                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ bgcolor: 'rgba(239, 69, 101, 0.1)', border: `1px solid ${THEME.danger}` }}>
                                <CardContent>
                                    <Typography variant="subtitle1" fontWeight="bold" color={THEME.danger} sx={{ mb: 1 }}>상황 1: 집값 폭등 시 (예: 15억)</Typography>
                                    <ul style={{ paddingLeft: '20px', margin: 0, fontSize: '0.9rem' }}>
                                        <li><b>결과:</b> 약속대로 11억에 팔아야 함.</li>
                                        <li><b>손해:</b> 15억까지 먹을 수 있었는데... (상승 이익 제한)</li>
                                        <li><b>이익:</b> 그래도 처음에 받은 <span style={{ color: THEME.success }}>1,000만원</span>은 내 돈.</li>
                                    </ul>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ bgcolor: 'rgba(44, 182, 125, 0.1)', border: `1px solid ${THEME.success}` }}>
                                <CardContent>
                                    <Typography variant="subtitle1" fontWeight="bold" color={THEME.success} sx={{ mb: 1 }}>상황 2: 집값 하락/횡보 시 (예: 9억)</Typography>
                                    <ul style={{ paddingLeft: '20px', margin: 0, fontSize: '0.9rem' }}>
                                        <li><b>결과:</b> 상대방은 아파트를 안 삼 (계약 무효).</li>
                                        <li><b>이익:</b> 집은 그대로 내 꺼 + <span style={{ color: THEME.success }}>1,000만원</span>도 챙김.</li>
                                        <li><b>효과:</b> 집값 하락분을 현금 보너스로 헷지(방어).</li>
                                    </ul>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Box>

                <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.1)' }} />

                {/* Step 2 */}
                <Box sx={{ mb: 5 }}>
                    <Typography variant="h5" fontWeight="bold" color={THEME.primary} sx={{ mb: 2 }}>2단계: JEPI와 JEPQ가 뭔가요?</Typography>
                    <Typography paragraph>
                        앞서 설명한 '커버드 콜 전략'을 아주 잘하는 <b>전문가(펀드매니저)가 대신 굴려주는 상품</b>입니다.
                    </Typography>
                    <ul style={{ paddingLeft: '20px' }}>
                        <li style={{ marginBottom: '8px' }}>복잡한 계약 직접 할 필요 없이, 이 주식(ETF)만 사면 알아서 매월 <b>현금 보너스</b>를 통장에 꽂아줍니다.</li>
                        <li>일반 배당주(연 1~2%)와 달리, 이 전략 덕분에 <b>연 8~12% 수준의 높은 배당</b>이 가능합니다.</li>
                    </ul>
                </Box>

                {/* Step 3 */}
                <Box sx={{ mb: 5 }}>
                    <Typography variant="h5" fontWeight="bold" color={THEME.primary} sx={{ mb: 2 }}>3단계: JEPI vs JEPQ 차이점</Typography>
                    <Typography sx={{ mb: 2 }}>둘 다 전략은 같지만, <b>'어떤 아파트(주식)'를 가지고 하느냐</b>의 차이입니다.</Typography>

                    <TableContainer component={Paper} sx={{ bgcolor: 'rgba(0,0,0,0.2)' }}>
                        <Table>
                            <TableHead>
                                <TableRow sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}>
                                    <TableCell sx={{ color: THEME.textDim }}>구분</TableCell>
                                    <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>JEPI (안정형)</TableCell>
                                    <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>JEPQ (성장형)</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                <TableRow>
                                    <TableCell sx={{ color: THEME.textDim }}>투자 대상</TableCell>
                                    <TableCell sx={{ color: THEME.text }}><b>S&P 500 (우량 기업)</b><br /><span style={{ fontSize: '0.8rem', color: THEME.textDim }}>MS, 비자, 마스터카드...</span></TableCell>
                                    <TableCell sx={{ color: THEME.text }}><b>나스닥 100 (기술주)</b><br /><span style={{ fontSize: '0.8rem', color: THEME.textDim }}>애플, 엔비디아, 테슬라...</span></TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell sx={{ color: THEME.textDim }}>성격</TableCell>
                                    <TableCell sx={{ color: THEME.text }}>주가가 묵직하게 움직임</TableCell>
                                    <TableCell sx={{ color: THEME.text }}>주가가 화끈하게 오르내림</TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell sx={{ color: THEME.textDim }}>배당률</TableCell>
                                    <TableCell sx={{ color: THEME.text }}>연 7~9%</TableCell>
                                    <TableCell sx={{ color: THEME.text }}>연 9~12% (변동성 높음)</TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>

                {/* Step 4 & 5 */}
                <Grid container spacing={4}>
                    <Grid item xs={12} md={6}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>👍 장점</Typography>
                        <Box sx={{ ml: 2 }}>
                            <Typography sx={{ mb: 1 }}>1. <b>매월 들어오는 현금</b>: 생활비/은퇴자금에 최고.</Typography>
                            <Typography sx={{ mb: 1 }}>2. <b>하락장 방어</b>: 주가가 빠져도 배당금이 손실을 메워줌.</Typography>
                            <Typography>3. <b>심리적 안정</b>: 횡보장에서도 배당 문자 받으면 든든함.</Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>👎 단점 (주의!)</Typography>
                        <Box sx={{ ml: 2 }}>
                            <Typography sx={{ mb: 1 }}>1. <b>상승장 소외감</b>: 불장일 때 남들보다 수익률이 낮습니다.<br /><span style={{ fontSize: '0.85rem', color: THEME.textDim }}>(15억 아파트를 11억에 파는 상황)</span></Typography>
                            <Typography>2. <b>원금 손실 가능</b>: 경제 위기로 주식 자체가 폭락하면 원금도 줄어듭니다.</Typography>
                        </Box>
                    </Grid>
                </Grid>

            </DialogContent>
            <DialogActions sx={{ p: 3, borderTop: '1px solid ' + THEME.border }}>
                <Button onClick={onClose} variant="contained" size="large" sx={{ bgcolor: THEME.primary, color: '#000', fontWeight: 'bold' }}>
                    이해했습니다
                </Button>
            </DialogActions>
        </Dialog>
    );
};

const MarketGuidePage: React.FC = () => {
    const [openCcGuide, setOpenCcGuide] = React.useState(false);

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            {/* Header Section */}
            <Box sx={{ mb: 6, textAlign: 'center' }}>
                <Typography variant="h3" fontWeight="bold" sx={{ mb: 2, background: `linear-gradient(45deg, ${THEME.primary}, ${THEME.secondary})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', wordKeepAll: 'break-word' }}>
                    2025년 12월 시장 전망 및 가이드
                </Typography>
                <Typography variant="h6" color={THEME.textDim} sx={{ wordKeepAll: 'break-word' }}>
                    AI 주도 기술주 강세 vs 고금리 채권 투자 막차 타기
                </Typography>
            </Box>

            {/* Key Themes */}
            <Grid container spacing={4} sx={{ mb: 6 }}>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, bgcolor: 'rgba(0, 209, 255, 0.05)', border: `1px solid ${THEME.primary}`, borderRadius: 2, height: '100%' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <TrendingUp sx={{ color: THEME.primary, fontSize: 32, mr: 2 }} />
                            <Typography variant="h5" fontWeight="bold">AI 주도의 기술주 강세</Typography>
                        </Box>
                        <Typography variant="body1" color={THEME.textDim} sx={{ mb: 2, wordKeepAll: 'break-word' }}>
                            변동성 속에서도 성장을 주도하는 빅테크(AI, 반도체, 데이터센터) 쏠림 현상이 뚜렷합니다.
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip label="엔비디아 (NVDA)" size="small" sx={{ bgcolor: 'rgba(0, 209, 255, 0.2)', color: THEME.primary }} />
                            <Chip label="마이크로소프트" size="small" sx={{ bgcolor: 'rgba(0, 209, 255, 0.2)', color: THEME.primary }} />
                            <Chip label="AI 반도체" size="small" sx={{ bgcolor: 'rgba(0, 209, 255, 0.2)', color: THEME.primary }} />
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, bgcolor: 'rgba(127, 90, 240, 0.05)', border: `1px solid ${THEME.secondary}`, borderRadius: 2, height: '100%' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <AccountBalance sx={{ color: THEME.secondary, fontSize: 32, mr: 2 }} />
                            <Typography variant="h5" fontWeight="bold">고금리 활용 채권 투자</Typography>
                        </Box>
                        <Typography variant="body1" color={THEME.textDim} sx={{ mb: 2, wordKeepAll: 'break-word' }}>
                            한국보다 높은 미국의 금리(4~5%)를 확정 짓기 위한 국채 및 회사채 매수 수요가 폭발하고 있습니다.
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip label="미국 국채 (Treasury)" size="small" sx={{ bgcolor: 'rgba(127, 90, 240, 0.2)', color: THEME.secondary }} />
                            <Chip label="월배당 (Monthly)" size="small" sx={{ bgcolor: 'rgba(127, 90, 240, 0.2)', color: THEME.secondary }} />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>

            {/* Section 1: US Stocks - Deep Dive */}
            <Box sx={{ mb: 8 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                    <Speed sx={{ mr: 2, color: THEME.primary }} /> 1. 미국 주식: 성장과 인컴의 조화
                </Typography>
                <Typography variant="body1" color={THEME.textDim} sx={{ mb: 4 }}>
                    초보자도 쉽게 이해할 수 있는 미국 주식 핵심 테마와 대표 상품 가이드입니다.
                </Typography>

                <Grid container spacing={4}>
                    {/* 1. Market Wide (Index) */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <TrendingUp sx={{ fontSize: 36, color: THEME.primary, mr: 2 }} />
                                <Box>
                                    <Typography variant="h5" fontWeight="bold">대표 지수 추종 (시장 전체)</Typography>
                                    <Typography variant="body2" color={THEME.textDim}>"미국 경제 전반에 분산 투자하는 가장 기본적인 방법"</Typography>
                                </Box>
                            </Box>
                            <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>S&P 500 (SPY / VOO)</Typography>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            미국 주식시장에 상장된 <b>상위 500개 우량 기업</b>에 투자합니다. 애플, MS, 아마존 등 1등 기업들이 모두 포함되어 있어, 개별 기업 분석이 어렵다면 가장 안전하고 확실한 선택입니다.<br />
                                            시장이 오르면 내 계좌도 같이 오르는 구조입니다.
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>나스닥 100 (QQQ / QQQM)</Typography>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            <b>기술주(Tech) 중심의 성장 기업 100개</b>에 집중 투자합니다. S&P 500보다 변동성은 크지만, 장기적으로 더 높은 기대 수익률을 보입니다.<br />
                                            AI, 반도체, IT 혁신 기업의 비중이 매우 높습니다.
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>

                    {/* 2. Tech & AI */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `1px solid ${THEME.warning}`, borderRadius: 2, boxShadow: '0 4px 20px rgba(255, 187, 40, 0.1)' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Speed sx={{ fontSize: 36, color: THEME.warning, mr: 2 }} />
                                <Box>
                                    <Typography variant="h5" fontWeight="bold" color={THEME.warning}>빅테크 및 AI 관련주</Typography>
                                    <Typography variant="body2" color={THEME.textDim}>"시장을 주도하는 혁신 기업에 집중 투자"</Typography>
                                </Box>
                            </Box>
                            <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>Magnificent 7 (M7)</Typography>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            현재 미국 시장을 하드캐리하고 있는 <b>7개의 초대형 기술주</b>를 의미합니다.<br />
                                            <span style={{ color: THEME.warning }}>엔비디아(NVDA), 마이크로소프트(MSFT), 애플(AAPL), 구글(GOOGL), 아마존(AMZN), 메타(META), 테슬라(TSLA)</span>
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>AI 인프라 & 반도체</Typography>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            AI 시대의 쌀과 같은 <b>반도체 섹터</b>에 투자합니다.<br />
                                            <b>SOXX</b> (필라델피아 반도체 지수 추종 ETF)가 대표적이며, 브로드컴(AVGO), AMD 같은 기업들이 포함됩니다.
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>

                    {/* 3. Dividend & Income */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `1px solid ${THEME.success}`, borderRadius: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <AttachMoney sx={{ fontSize: 36, color: THEME.success, mr: 2 }} />
                                <Box>
                                    <Typography variant="h5" fontWeight="bold" color={THEME.success}>배당 및 인컴 (현금 흐름)</Typography>
                                    <Typography variant="body2" color={THEME.textDim}>"주가 상승보다 안정적인 월/분기 배당을 선호하는 투자자"</Typography>
                                </Box>
                            </Box>
                            <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                            <Typography variant="h6" fontWeight="bold" color={THEME.text} sx={{ mr: 1 }}>SCHD</Typography>
                                            <Chip label="배당 성장" size="small" sx={{ bgcolor: 'rgba(44, 182, 125, 0.2)', color: THEME.success, fontSize: '0.7rem' }} />
                                        </div>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            <b>"한국인이 가장 사랑하는 배당 ETF"</b><br />
                                            10년 이상 배당금을 꾸준히 늘려온 우량 기업 100개에 투자합니다. 배당금도 받고 주가 상승도 기대할 수 있는 <b>'배당 성장'</b> 전략의 대표주자입니다.
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                            <Typography variant="h6" fontWeight="bold" color={THEME.text} sx={{ mr: 1 }}>JEPI / JEPQ</Typography>
                                            <Chip label="월배당 8~10%" size="small" sx={{ bgcolor: 'rgba(44, 182, 125, 0.2)', color: THEME.success, fontSize: '0.7rem' }} />
                                        </div>
                                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 1, lineHeight: 1.6 }}>
                                            <b>"커버드콜 전략"</b>을 사용하여 주가가 횡보하더라도 높은 배당 수익을 추구합니다.<br />
                                            <b>JEPI</b>는 S&P500 기반, <b>JEPQ</b>는 나스닥 기반입니다. 매월 월급처럼 배당을 받고 싶은 은퇴자에게 인기가 높습니다.
                                        </Typography>
                                        <Button
                                            variant="outlined"
                                            size="small"
                                            fullWidth
                                            sx={{ mt: 2, borderColor: THEME.success, color: THEME.success, textTransform: 'none' }}
                                            onClick={() => setOpenCcGuide(true)}
                                        >
                                            초보자를 위한 "커버드콜" 완벽 가이드 보기
                                        </Button>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>
                </Grid>
            </Box>

            {/* Section 2: US Bonds */}
            <Box sx={{ mb: 8 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                    <AttachMoney sx={{ mr: 2, color: THEME.secondary }} /> 2. 미국 채권: 고금리 막차 타기
                </Typography>
                <Grid container spacing={3}>
                    {/* Treasury */}
                    <Grid item xs={12} md={6}>
                        <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}` }}>
                            <CardContent>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>미국 국채 (US Treasury)</Typography>
                                <Typography variant="body2" color={THEME.textDim} sx={{ mb: 2 }}>
                                    미국 정부가 보증하는 가장 안전한 자산입니다.
                                </Typography>
                                <TableContainer>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.textDim }}>구분</TableCell>
                                                <TableCell sx={{ color: THEME.textDim }}>티커 (Ticker)</TableCell>
                                                <TableCell sx={{ color: THEME.textDim }}>특징</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.text }}>초단기채 (파킹)</TableCell>
                                                <TableCell sx={{ color: THEME.success, fontWeight: 'bold' }}>SGOV, SHV</TableCell>
                                                <TableCell sx={{ color: THEME.text }}>연 4%대 이자, 현금 대용</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.text }}>중장기채</TableCell>
                                                <TableCell sx={{ color: THEME.secondary, fontWeight: 'bold' }}>TLT, IEF</TableCell>
                                                <TableCell sx={{ color: THEME.text }}>금리 인하 시 시세 차익 기대</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Corporate */}
                    <Grid item xs={12} md={6}>
                        <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}` }}>
                            <CardContent>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>회사채 (Corporate Bonds)</Typography>
                                <Typography variant="body2" color={THEME.textDim} sx={{ mb: 2 }}>
                                    국채보다 위험하지만 더 높은 이자 수익을 추구합니다.
                                </Typography>
                                <TableContainer>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.textDim }}>구분</TableCell>
                                                <TableCell sx={{ color: THEME.textDim }}>티커 (Ticker)</TableCell>
                                                <TableCell sx={{ color: THEME.textDim }}>리스크/수익</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.text }}>투자등급 (우량)</TableCell>
                                                <TableCell sx={{ color: THEME.primary, fontWeight: 'bold' }}>LQD</TableCell>
                                                <TableCell sx={{ color: THEME.text }}>애플 등 우량 기업 채권</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.text }}>하이일드 (고수익)</TableCell>
                                                <TableCell sx={{ color: THEME.danger, fontWeight: 'bold' }}>HYG</TableCell>
                                                <TableCell sx={{ color: THEME.text }}>높은 이자, 신용 위험 존재</TableCell>
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            {/* Personalized Recommendation System */}
            <Box sx={{ mb: 8 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                    <Speed sx={{ mr: 2, color: THEME.secondary }} /> 3. 나에게 딱 맞는 상품 찾기 (AI 진단)
                </Typography>
                <RecommendationSection />
            </Box>

            {/* Summary Strategy */}
            <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>투자 성향별 요약 및 추천</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow sx={{ '& th': { color: THEME.textDim, fontWeight: 'bold' } }}>
                                <TableCell>투자 성향</TableCell>
                                <TableCell>추천 상품군 (티커)</TableCell>
                                <TableCell>핵심 포인트</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>안정 추구 (현금 보관)</TableCell>
                                <TableCell sx={{ color: THEME.text }}>SGOV, SHV</TableCell>
                                <TableCell sx={{ color: THEME.textDim }}>달러를 놀리지 않고 연 4~5% 이자 수취</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>시장 대표지수 (장기)</TableCell>
                                <TableCell sx={{ color: THEME.text }}>SPY, VOO, QQQ</TableCell>
                                <TableCell sx={{ color: THEME.textDim }}>미국 경제 성장에 베팅 (연금 등)</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>현금 흐름 (월세 효과)</TableCell>
                                <TableCell sx={{ color: THEME.text }}>JEPI, SCHD, 리얼티인컴(O)</TableCell>
                                <TableCell sx={{ color: THEME.textDim }}>매월/분기별 달러 배당금 수취</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell sx={{ color: THEME.text, fontWeight: 'bold' }}>금리 인하 베팅</TableCell>
                                <TableCell sx={{ color: THEME.text }}>TLT, TMF(3배)</TableCell>
                                <TableCell sx={{ color: THEME.textDim }}>금리 하락 시 시세 차익 극대화 (변동성 주의)</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Educational Modal */}
            <DetailedGuideDialog open={openCcGuide} onClose={() => setOpenCcGuide(false)} />
        </Box>

    );
};

export default MarketGuidePage;
