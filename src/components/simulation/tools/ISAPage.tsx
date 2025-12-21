import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, TextField, Slider, Button, Alert } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    success: 'var(--ipc-success)',
    warning: 'var(--ipc-warning)',
    danger: 'var(--ipc-danger)',
    border: 'var(--ipc-border)'
};

const ISAPage: React.FC = () => {
    // State for calculation
    const [principal, setPrincipal] = useState<number>(20000000); // 2000 Man Won (Annual Max)
    const [years, setYears] = useState<number>(3);
    const [returnRate, setReturnRate] = useState<number>(5); // 5%

    // Constants
    const TAX_RATE_NORMAL = 0.154; // 15.4%
    const TAX_RATE_ISA_LOWER = 0.099; // 9.9% (for excess)
    const EXEMPTION_LIMIT = 2000000; // 200 Man Won

    // Calculation Logic
    const calculateTax = () => {
        const totalInvestment = principal * years;
        const finalValue = totalInvestment * Math.pow(1 + returnRate / 100, years); // Simplified Compound
        const profit = finalValue - totalInvestment;

        // General Account Tax
        const generalTax = profit * TAX_RATE_NORMAL;
        const generalNetProfit = profit - generalTax;

        // ISA Account Tax
        let isaTax = 0;
        if (profit > EXEMPTION_LIMIT) {
            isaTax = (profit - EXEMPTION_LIMIT) * TAX_RATE_ISA_LOWER;
        }
        const isaNetProfit = profit - isaTax;

        return [
            {
                name: '일반 계좌',
                Tax: Math.round(generalTax),
                NetProfit: Math.round(generalNetProfit),
                Total: Math.round(generalTax + generalNetProfit)
            },
            {
                name: 'ISA 계좌',
                Tax: Math.round(isaTax),
                NetProfit: Math.round(isaNetProfit),
                Total: Math.round(isaTax + isaNetProfit)
            }
        ];
    };

    const data = calculateTax();

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 2 }}>
                ISA (개인종합자산관리계좌)
            </Typography>
            <Typography variant="body1" sx={{ color: THEME.textDim, mb: 4 }}>
                일반 계좌 대비 ISA 계좌 활용 시 예상되는 절세 혜택을 시뮬레이션합니다.
            </Typography>

            <Grid container spacing={4}>
                {/* Input Panel */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>시뮬레이션 설정</Typography>

                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>연간 납입금 (원)</Typography>
                            <TextField
                                fullWidth
                                type="number"
                                value={principal}
                                onChange={(e) => setPrincipal(Number(e.target.value))}
                                sx={{ bgcolor: '#f5f5f5' }}
                            />
                            <Typography variant="caption" color={THEME.textDim}>연간 최대 2,000만원</Typography>
                        </Box>

                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>투자 기간 (년): {years}년</Typography>
                            <Slider
                                value={years}
                                onChange={(_, v) => setYears(v as number)}
                                min={3} max={10} step={1}
                                sx={{ color: THEME.primary }}
                            />
                        </Box>

                        <Box sx={{ mb: 3 }}>
                            <Typography gutterBottom>예상 수익률 (%): {returnRate}%</Typography>
                            <Slider
                                value={returnRate}
                                onChange={(_, v) => setReturnRate(v as number)}
                                min={1} max={20} step={0.5}
                                sx={{ color: THEME.warning }}
                            />
                        </Box>

                        <Alert severity="info" sx={{ bgcolor: 'rgba(0, 209, 255, 0.1)', color: THEME.text }}>
                            ISA는 200만원까지 비과세, 초과 수익은 9.9% 분리과세 적용.
                        </Alert>
                    </Paper>
                </Grid>

                {/* Result Chart */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: '100%' }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>세금 및 순수익 비교</Typography>

                        <Box sx={{ height: 400, width: '100%' }}>
                            <ResponsiveContainer>
                                <BarChart data={data} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" horizontal={false} />
                                    <XAxis type="number" stroke={THEME.textDim} tickFormatter={(val) => `₩${(val / 10000).toLocaleString()}만`} />
                                    <YAxis dataKey="name" type="category" stroke={THEME.textDim} width={120} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                        formatter={(val: number) => `₩${val.toLocaleString()}`}
                                    />
                                    <Legend />
                                    <Bar dataKey="NetProfit" stackId="a" fill={THEME.success} name="순수익" />
                                    <Bar dataKey="Tax" stackId="a" fill={THEME.danger} name="예상 세금" />
                                </BarChart>
                            </ResponsiveContainer>
                        </Box>

                        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 4 }}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="caption" color={THEME.textDim}>절세 금액</Typography>
                                <Typography variant="h4" fontWeight="bold" color={THEME.primary}>
                                    ₩{(data[0].Tax - data[1].Tax).toLocaleString()}
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default ISAPage;
