import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, TextField, Slider, Alert, Card, CardContent, IconButton, Stack } from '@mui/material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Add, Remove } from '@mui/icons-material';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    secondary: 'var(--ipc-secondary)',
    success: 'var(--ipc-success)',
    danger: 'var(--ipc-danger)',
    border: 'var(--ipc-border)'
};

const PensionPage: React.FC = () => {
    // State
    const [currentAge, setCurrentAge] = useState<number>(30);
    const [retireAge, setRetireAge] = useState<number>(60);
    const [currentSavings, setCurrentSavings] = useState<number>(10000000); // 1,000 Man Won
    const [monthlyContribution, setMonthlyContribution] = useState<number>(300000); // 30 Man Won
    const [returnRate, setReturnRate] = useState<number>(4);

    // National Pension State
    const [nationalPension, setNationalPension] = useState<number>(1000000); // 100 Man Won
    const [startPensionAge, setStartPensionAge] = useState<number>(65);

    // Calculate Projection
    const calculateProjection = () => {
        const data = [];
        let balance = currentSavings;
        const months = (Math.max(retireAge, startPensionAge) + 10 - currentAge) * 12; // Project until +10 years after pension start for viz

        for (let i = 0; i <= months; i += 12) { // Yearly data points
            const year = currentAge + (i / 12);
            // Stop contributing after retirement
            if (year < retireAge) {
                balance = (balance + (monthlyContribution * 12)) * (1 + returnRate / 100);
            } else {
                // After retirement, just grow by return rate (or withdraw - simplified here)
                balance = balance * (1 + returnRate / 100);
            }

            data.push({
                age: year,
                balance: Math.round(balance)
            });
        }
        return data.filter(d => d.age <= 80); // Cap visualization at 80
    };

    const data = calculateProjection();
    // Final Amount at Retirement Age (approximate for display)
    const retirementPoint = data.find(d => Math.floor(d.age) === retireAge);
    const finalAmount = retirementPoint ? retirementPoint.balance : 0;

    // Simple 4% withdrawal rule estimation (monthly)
    const personalPension = Math.round((finalAmount * 0.04) / 12);
    const totalMonthlyPension = personalPension + nationalPension;

    // Helper for Stepper Style
    const StepperControl = ({ onDec, onInc, children }: { onDec: () => void, onInc: () => void, children: React.ReactNode }) => (
        <Stack direction="row" spacing={1} alignItems="center">
            <IconButton onClick={onDec} size="small" sx={{ bgcolor: '#f5f5f5', borderRadius: 1, '&:hover': { bgcolor: '#e0e0e0' } }}>
                <Remove fontSize="small" />
            </IconButton>
            <Box sx={{ flex: 1 }}>{children}</Box>
            <IconButton onClick={onInc} size="small" sx={{ bgcolor: '#f5f5f5', borderRadius: 1, '&:hover': { bgcolor: '#e0e0e0' } }}>
                <Add fontSize="small" />
            </IconButton>
        </Stack>
    );

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 2 }}>
                퇴직연금 & 국민연금 시뮬레이션
            </Typography>
            <Typography variant="body1" sx={{ color: THEME.textDim, mb: 4 }}>
                퇴직연금(IRP/DC)과 국민연금을 더해 은퇴 후 월 현금 흐름을 계산합니다.
            </Typography>

            <Grid container spacing={4}>
                {/* Inputs */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>나의 플랜</Typography>

                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>현재 나이: {currentAge}세</Typography>
                            <StepperControl
                                onDec={() => setCurrentAge(Math.max(20, currentAge - 1))}
                                onInc={() => setCurrentAge(Math.min(60, currentAge + 1))}
                            >
                                <Slider value={currentAge} onChange={(_, v) => setCurrentAge(v as number)} min={20} max={60} />
                            </StepperControl>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>은퇴 나이: {retireAge}세</Typography>
                            <StepperControl
                                onDec={() => setRetireAge(Math.max(50, retireAge - 1))}
                                onInc={() => setRetireAge(Math.min(70, retireAge + 1))}
                            >
                                <Slider value={retireAge} onChange={(_, v) => setRetireAge(v as number)} min={50} max={70} />
                            </StepperControl>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>월 납입금 (개인연금)</Typography>
                            <StepperControl
                                onDec={() => setMonthlyContribution(Math.max(0, monthlyContribution - 10000))} // -1 Man
                                onInc={() => setMonthlyContribution(monthlyContribution + 10000)} // +1 Man
                            >
                                <TextField
                                    fullWidth type="text"
                                    value={monthlyContribution.toLocaleString()}
                                    onChange={(e) => {
                                        const val = Number(e.target.value.replace(/,/g, ''));
                                        if (!isNaN(val)) setMonthlyContribution(val);
                                    }}
                                    sx={{ bgcolor: '#f5f5f5', input: { color: THEME.text, textAlign: 'center' } }}
                                />
                            </StepperControl>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>현재 모은 돈 (원)</Typography>
                            <StepperControl
                                onDec={() => setCurrentSavings(Math.max(0, currentSavings - 1000000))} // -100 Man
                                onInc={() => setCurrentSavings(currentSavings + 1000000)} // +100 Man
                            >
                                <TextField
                                    fullWidth type="text"
                                    value={currentSavings.toLocaleString()}
                                    onChange={(e) => {
                                        const val = Number(e.target.value.replace(/,/g, ''));
                                        if (!isNaN(val)) setCurrentSavings(val);
                                    }}
                                    sx={{ bgcolor: '#f5f5f5', input: { color: THEME.text, textAlign: 'center' } }}
                                />
                            </StepperControl>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>기대 수익률: {returnRate}%</Typography>
                            <StepperControl
                                onDec={() => setReturnRate(Math.max(0, returnRate - 0.5))}
                                onInc={() => setReturnRate(Math.min(20, returnRate + 0.5))}
                            >
                                <Slider value={returnRate} onChange={(_, v) => setReturnRate(v as number)} min={1} max={10} step={0.5} sx={{ color: THEME.secondary }} />
                            </StepperControl>
                        </Box>

                        <Alert severity="info" sx={{ bgcolor: 'rgba(0, 209, 255, 0.1)', color: THEME.text, border: `1px solid ${THEME.primary}` }}>
                            <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1, color: THEME.primary }}>국민연금 설정</Typography>
                            <Box sx={{ mb: 2 }}>
                                <Typography gutterBottom fontSize="0.9rem">예상 수령액 (월)</Typography>
                                <StepperControl
                                    onDec={() => setNationalPension(Math.max(0, nationalPension - 100000))} // -10 Man
                                    onInc={() => setNationalPension(nationalPension + 100000)} // +10 Man
                                >
                                    <TextField
                                        fullWidth size="small" type="text"
                                        value={nationalPension.toLocaleString()}
                                        onChange={(e) => {
                                            const val = Number(e.target.value.replace(/,/g, ''));
                                            if (!isNaN(val)) setNationalPension(val);
                                        }}
                                        sx={{ bgcolor: '#f5f5f5', input: { color: THEME.text, textAlign: 'center' } }}
                                    />
                                </StepperControl>
                            </Box>
                            <Box>
                                <Typography gutterBottom fontSize="0.9rem">수령 개시 나이: {startPensionAge}세</Typography>
                                <StepperControl
                                    onDec={() => setStartPensionAge(Math.max(55, startPensionAge - 1))}
                                    onInc={() => setStartPensionAge(Math.min(75, startPensionAge + 1))}
                                >
                                    <Slider value={startPensionAge} onChange={(_, v) => setStartPensionAge(v as number)} min={60} max={70} sx={{ color: THEME.primary }} />
                                </StepperControl>
                            </Box>
                        </Alert>
                    </Paper>
                </Grid>

                {/* Dashboard */}
                <Grid item xs={12} md={8}>
                    <Grid container spacing={3} sx={{ mb: 3 }}>
                        <Grid item xs={12} sm={6}>
                            <Card sx={{ bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                                <CardContent>
                                    <Typography color={THEME.textDim} variant="caption">{retireAge}세 시점 예상 개인연금 자산</Typography>
                                    <Typography variant="h5" fontWeight="bold" color={THEME.primary}>
                                        ₩{finalAmount.toLocaleString()}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <Card sx={{ bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                                <CardContent>
                                    <Typography color={THEME.textDim} variant="caption">은퇴 후 월 예상 현금흐름 (Total)</Typography>
                                    <Typography variant="h4" fontWeight="bold" color={THEME.success}>
                                        ₩{totalMonthlyPension.toLocaleString()}
                                    </Typography>
                                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                                        <Typography variant="caption" color={THEME.secondary}>
                                            개인: ₩{personalPension.toLocaleString()}
                                        </Typography>
                                        <Typography variant="caption" color={THEME.primary}>
                                            국민: ₩{nationalPension.toLocaleString()}
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: 400 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>자산 성장 시뮬레이션</Typography>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <defs>
                                    <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={THEME.primary} stopOpacity={0.8} />
                                        <stop offset="95%" stopColor={THEME.primary} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="age" stroke={THEME.textDim} />
                                <YAxis tickFormatter={(val) => `₩${(val / 100000000).toFixed(1)}억`} stroke={THEME.textDim} width={80} />
                                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                                <Tooltip formatter={(val: number) => `₩${val.toLocaleString()}`} contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }} />
                                <Area type="monotone" dataKey="balance" stroke={THEME.primary} fillOpacity={1} fill="url(#colorPv)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Paper>

                    {retireAge < startPensionAge && (
                        <Alert severity="warning" sx={{ mt: 3, bgcolor: 'rgba(239, 69, 101, 0.1)', color: '#ff8a8a', border: `1px solid ${THEME.danger}` }}>
                            <Typography variant="subtitle2" fontWeight="bold">⚠️ 소득 공백기 (Income Crevasse) 주의!</Typography>
                            <Typography variant="body2">
                                은퇴({retireAge}세) 후 국민연금 수령({startPensionAge}세) 전까지 <b>{startPensionAge - retireAge}년</b> 동안은 개인연금(월 {personalPension.toLocaleString()}원)으로만 생활해야 합니다.
                            </Typography>
                        </Alert>
                    )}
                </Grid>
            </Grid>
        </Box>
    );
};

export default PensionPage;
