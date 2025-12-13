import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Select, MenuItem, Stack } from '@mui/material';
import { Delete, Add, MoneyOff, ReportProblem } from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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

interface Loan {
    id: number;
    name: string;
    principal: number;
    rate: number;
    term: number; // months
    paymentType: 'amortization' | 'interest_only';
}

const DebtManagement: React.FC = () => {
    const [loans, setLoans] = useState<Loan[]>([
        { id: 1, name: '주택담보대출', principal: 300000000, rate: 4.5, term: 360, paymentType: 'amortization' },
        { id: 2, name: '신용대출', principal: 50000000, rate: 6.2, term: 60, paymentType: 'amortization' }
    ]);

    const [newLoan, setNewLoan] = useState<Omit<Loan, 'id'>>({
        name: '', principal: 0, rate: 5.0, term: 120, paymentType: 'amortization'
    });

    // Helper: Calculate Monthly Payment (PMT)
    const calculatePMT = (loan: Loan) => {
        const r = loan.rate / 100 / 12;
        const n = loan.term;
        if (loan.paymentType === 'interest_only') {
            return loan.principal * r;
        } else {
            if (r === 0) return loan.principal / n;
            return (loan.principal * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
        }
    };

    const handleAdd = () => {
        if (!newLoan.name || newLoan.principal <= 0) return;
        setLoans([...loans, { ...newLoan, id: Date.now() }]);
        setNewLoan({ name: '', principal: 0, rate: 5.0, term: 120, paymentType: 'amortization' });
    };

    const handleDelete = (id: number) => {
        setLoans(loans.filter(l => l.id !== id));
    };

    // Calculate Aggregates
    const totalDebt = loans.reduce((sum, l) => sum + l.principal, 0);
    const totalMonthlyPayment = loans.reduce((sum, l) => sum + calculatePMT(l), 0);

    // Chart Data (Amortization Schedule for Total Debt - Simplified)
    const generateChartData = () => {
        const data = [];
        const maxTerm = Math.max(...loans.map(l => l.term), 0);
        let currentLoans = loans.map(l => ({ ...l, currentBalance: l.principal }));

        for (let i = 0; i <= Math.min(maxTerm, 120); i += 12) { // Show up to 10 years or max term, yearly steps
            const year = i / 12;
            const totalBalance = currentLoans.reduce((sum, l) => sum + l.currentBalance, 0);

            data.push({ year, balance: Math.round(totalBalance) });

            // Simulate 12 months passing
            for (let month = 0; month < 12; month++) {
                currentLoans.forEach(l => {
                    if (l.currentBalance > 0) {
                        const r = l.rate / 100 / 12;
                        const interest = l.currentBalance * r;
                        const payment = calculatePMT(l);
                        const principalPaid = payment - interest;
                        if (l.paymentType === 'amortization') {
                            l.currentBalance = Math.max(0, l.currentBalance - principalPaid);
                        }
                    }
                });
            }
        }
        return data;
    };

    const chartData = generateChartData();

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <MoneyOff sx={{ fontSize: 36, color: THEME.danger }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">부채 관리 및 상환 계획</Typography>
                    <Typography variant="body1" color={THEME.textDim}>대출 현황을 파악하고 월 상환 부담과 부채 감소 추이를 시뮬레이션합니다.</Typography>
                </Box>
            </Box>

            <Grid container spacing={4}>
                {/* Inputs */}
                <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>대출 추가</Typography>
                        <Stack spacing={3}>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>대출명</Typography>
                                <TextField
                                    fullWidth size="small"
                                    value={newLoan.name} onChange={(e) => setNewLoan({ ...newLoan, name: e.target.value })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                />
                            </Box>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>원금 (원)</Typography>
                                <TextField
                                    type="number" fullWidth size="small"
                                    value={newLoan.principal} onChange={(e) => setNewLoan({ ...newLoan, principal: Number(e.target.value) })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                />
                            </Box>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color={THEME.textDim}>이자율 (%)</Typography>
                                    <TextField
                                        type="number" fullWidth size="small"
                                        value={newLoan.rate} onChange={(e) => setNewLoan({ ...newLoan, rate: Number(e.target.value) })}
                                        sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color={THEME.textDim}>기간 (개월)</Typography>
                                    <TextField
                                        type="number" fullWidth size="small"
                                        value={newLoan.term} onChange={(e) => setNewLoan({ ...newLoan, term: Number(e.target.value) })}
                                        sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                    />
                                </Grid>
                            </Grid>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>상환 방식</Typography>
                                <Select
                                    fullWidth size="small"
                                    value={newLoan.paymentType} onChange={(e) => setNewLoan({ ...newLoan, paymentType: e.target.value as any })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                >
                                    <MenuItem value="amortization">원리금균등상환</MenuItem>
                                    <MenuItem value="interest_only">만기일시상환 (이자만)</MenuItem>
                                </Select>
                            </Box>
                            <Button
                                variant="contained" fullWidth
                                onClick={handleAdd}
                                sx={{ bgcolor: THEME.danger, color: '#fff', fontWeight: 'bold' }}
                                startIcon={<Add />}
                            >
                                대출 추가
                            </Button>
                        </Stack>
                    </Paper>

                    <Box sx={{ mt: 3 }}>
                        <Card sx={{ bgcolor: 'rgba(239, 69, 101, 0.1)', border: `1px solid ${THEME.danger}` }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                                    <ReportProblem sx={{ color: THEME.danger }} />
                                    <Typography variant="h6" fontWeight="bold" color={THEME.danger}>월 총 상환액 (예상)</Typography>
                                </Box>
                                <Typography variant="h4" fontWeight="bold">₩{Math.round(totalMonthlyPayment).toLocaleString()}</Typography>
                                <Typography variant="body2" color={THEME.danger} sx={{ mt: 1 }}>
                                    (총 부채: ₩{Math.round(totalDebt).toLocaleString()})
                                </Typography>
                            </CardContent>
                        </Card>
                    </Box>
                </Grid>

                {/* List & Chart */}
                <Grid item xs={12} md={7}>
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>보유 대출 목록</Typography>
                                <TableContainer sx={{ maxHeight: 300 }}>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.textDim }}>이름</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>잔액</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>금리</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>월 상환액</TableCell>
                                                <TableCell align="center" sx={{ color: THEME.textDim }}>관리</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {loans.map((loan) => (
                                                <TableRow key={loan.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                                    <TableCell component="th" scope="row" sx={{ color: THEME.text }}>{loan.name}</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.text }}>{loan.principal.toLocaleString()}</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.danger }}>{loan.rate}%</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.text, fontWeight: 'bold' }}>{Math.round(calculatePMT(loan)).toLocaleString()}</TableCell>
                                                    <TableCell align="center">
                                                        <IconButton size="small" onClick={() => handleDelete(loan.id)} sx={{ color: THEME.textDim }}>
                                                            <Delete fontSize="small" />
                                                        </IconButton>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                            {loans.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={5} align="center" sx={{ color: THEME.textDim, py: 4 }}>등록된 대출이 없습니다.</TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Paper>
                        </Grid>
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, height: 350 }}>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>부채 상환 시뮬레이션 (10년)</Typography>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorDebt" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor={THEME.danger} stopOpacity={0.8} />
                                                <stop offset="95%" stopColor={THEME.danger} stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <XAxis dataKey="year" stroke={THEME.textDim} tickFormatter={(val) => `${val}년후`} />
                                        <YAxis stroke={THEME.textDim} tickFormatter={(val) => `₩${(val / 100000000).toFixed(1)}억`} />
                                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: THEME.bg, border: `1px solid ${THEME.border}` }}
                                            formatter={(value: number) => `₩${value.toLocaleString()}`}
                                            labelFormatter={(l) => `${l}년 후 잔액`}
                                        />
                                        <Area type="monotone" dataKey="balance" stroke={THEME.danger} fillOpacity={1} fill="url(#colorDebt)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </Paper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Box>
    );
};

export default DebtManagement;
