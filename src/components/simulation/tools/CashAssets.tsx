import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Select, MenuItem, Stack } from '@mui/material';
import { Delete, Add, TrendingUp, AccountBalanceWallet } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

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

interface Asset {
    id: number;
    name: string;
    type: 'deposit' | 'savings'; // deposit (Ye-Geum), savings (Jeok-Geum)
    amount: number; // Principal or Monthly Contribution
    rate: number;
    duration: number; // months
}

const CashAssets: React.FC = () => {
    const [assets, setAssets] = useState<Asset[]>([
        { id: 1, name: '정기예금 A', type: 'deposit', amount: 50000000, rate: 3.5, duration: 12 },
        { id: 2, name: '월 적금 B', type: 'savings', amount: 1000000, rate: 4.2, duration: 24 }
    ]);

    const [newAsset, setNewAsset] = useState<Omit<Asset, 'id'>>({
        name: '', type: 'deposit', amount: 0, rate: 3.0, duration: 12
    });

    // Helper: Calculate Maturity Amount
    const calculateMaturity = (asset: Asset) => {
        if (asset.type === 'deposit') {
            // Simple Interest
            const interest = asset.amount * (asset.rate / 100) * (asset.duration / 12);
            return asset.amount + interest;
        } else {
            // Monthly Savings (Simplified)
            const n = asset.duration;
            const totalPrincipal = asset.amount * n;
            // Simple Interest for monthly savings: P * r * (n+1)/24
            const interest = totalPrincipal * (asset.rate / 100) * ((n + 1) / 24);
            return totalPrincipal + interest;
        }
    };

    const handleAdd = () => {
        if (!newAsset.name || newAsset.amount <= 0) return;
        setAssets([...assets, { ...newAsset, id: Date.now() }]);
        setNewAsset({ name: '', type: 'deposit', amount: 0, rate: 3.0, duration: 12 });
    };

    const handleDelete = (id: number) => {
        setAssets(assets.filter(a => a.id !== id));
    };

    // Visualization Data
    const totalPrincipal = assets.reduce((sum, a) => sum + (a.type === 'deposit' ? a.amount : a.amount * a.duration), 0);
    const totalMaturity = assets.reduce((sum, a) => sum + calculateMaturity(a), 0);
    const totalProfit = totalMaturity - totalPrincipal;

    const chartData = assets.map(a => ({
        name: a.name,
        Principal: Math.round(a.type === 'deposit' ? a.amount : a.amount * a.duration),
        Interest: Math.round(calculateMaturity(a) - (a.type === 'deposit' ? a.amount : a.amount * a.duration))
    }));

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalanceWallet sx={{ fontSize: 36, color: THEME.primary }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">현금 및 안전자산 관리</Typography>
                    <Typography variant="body1" color={THEME.textDim}>예적금 포트폴리오를 관리하고 만기 예상 금액을 시뮬레이션합니다.</Typography>
                </Box>
            </Box>

            <Grid container spacing={4}>
                {/* Input Panel */}
                <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>자산 추가</Typography>

                        <Stack spacing={3}>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>상품명</Typography>
                                <TextField
                                    fullWidth size="small"
                                    value={newAsset.name} onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                />
                            </Box>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color={THEME.textDim}>유형</Typography>
                                    <Select
                                        fullWidth size="small"
                                        value={newAsset.type} onChange={(e) => setNewAsset({ ...newAsset, type: e.target.value as any })}
                                        sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                    >
                                        <MenuItem value="deposit">정기예금 (거치식)</MenuItem>
                                        <MenuItem value="savings">정기적금 (적립식)</MenuItem>
                                    </Select>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="caption" color={THEME.textDim}>기간 (개월)</Typography>
                                    <TextField
                                        type="number" fullWidth size="small"
                                        value={newAsset.duration} onChange={(e) => setNewAsset({ ...newAsset, duration: Number(e.target.value) })}
                                        sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                    />
                                </Grid>
                            </Grid>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>
                                    {newAsset.type === 'deposit' ? '예치 금액 (원)' : '월 납입 금액 (원)'}
                                </Typography>
                                <TextField
                                    type="number" fullWidth size="small"
                                    value={newAsset.amount} onChange={(e) => setNewAsset({ ...newAsset, amount: Number(e.target.value) })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                />
                            </Box>
                            <Box>
                                <Typography variant="caption" color={THEME.textDim}>연 이자율 (%)</Typography>
                                <TextField
                                    type="number" fullWidth size="small"
                                    value={newAsset.rate} onChange={(e) => setNewAsset({ ...newAsset, rate: Number(e.target.value) })}
                                    sx={{ bgcolor: 'rgba(255,255,255,0.05)' }}
                                />
                            </Box>
                            <Button
                                variant="contained" fullWidth
                                onClick={handleAdd}
                                sx={{ bgcolor: THEME.primary, color: '#000', fontWeight: 'bold' }}
                                startIcon={<Add />}
                            >
                                자산 추가
                            </Button>
                        </Stack>
                    </Paper>

                    <Box sx={{ mt: 3 }}>
                        <Card sx={{ bgcolor: 'rgba(44, 182, 125, 0.1)', border: `1px solid ${THEME.success}` }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                                    <TrendingUp sx={{ color: THEME.success }} />
                                    <Typography variant="h6" fontWeight="bold" color={THEME.success}>만기 예상 총액</Typography>
                                </Box>
                                <Typography variant="h4" fontWeight="bold">₩{Math.round(totalMaturity).toLocaleString()}</Typography>
                                <Typography variant="body2" color={THEME.success} sx={{ mt: 1 }}>
                                    (세전 이자수익 + ₩{Math.round(totalProfit).toLocaleString()})
                                </Typography>
                            </CardContent>
                        </Card>
                    </Box>
                </Grid>

                {/* List & Chart */}
                <Grid item xs={12} md={7}>
                    <Grid container spacing={3} sx={{ mb: 3 }}>
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>보유 자산 목록</Typography>
                                <TableContainer sx={{ maxHeight: 300 }}>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: THEME.textDim }}>이름</TableCell>
                                                <TableCell sx={{ color: THEME.textDim }}>유형</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>금액/월납입</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>금리</TableCell>
                                                <TableCell align="right" sx={{ color: THEME.textDim }}>만기액</TableCell>
                                                <TableCell align="center" sx={{ color: THEME.textDim }}>관리</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {assets.map((asset) => (
                                                <TableRow key={asset.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                                    <TableCell component="th" scope="row" sx={{ color: THEME.text }}>{asset.name}</TableCell>
                                                    <TableCell sx={{ color: THEME.textDim }}>{asset.type === 'deposit' ? '예금' : '적금'}</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.text }}>{asset.amount.toLocaleString()}</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.secondary }}>{asset.rate}%</TableCell>
                                                    <TableCell align="right" sx={{ color: THEME.success, fontWeight: 'bold' }}>{Math.round(calculateMaturity(asset)).toLocaleString()}</TableCell>
                                                    <TableCell align="center">
                                                        <IconButton size="small" onClick={() => handleDelete(asset.id)} sx={{ color: THEME.danger }}>
                                                            <Delete fontSize="small" />
                                                        </IconButton>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                            {assets.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={6} align="center" sx={{ color: THEME.textDim, py: 4 }}>등록된 자산이 없습니다.</TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Paper>
                        </Grid>
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, height: 350 }}>
                                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>자산 구성 및 이자 수익</Typography>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#333" />
                                        <XAxis type="number" stroke={THEME.textDim} />
                                        <YAxis dataKey="name" type="category" stroke={THEME.textDim} width={100} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: THEME.bg, border: `1px solid ${THEME.border}` }}
                                            formatter={(value: number) => `₩${value.toLocaleString()}`}
                                        />
                                        <Legend />
                                        <Bar dataKey="Principal" stackId="a" fill={THEME.primary} name="원금" />
                                        <Bar dataKey="Interest" stackId="a" fill={THEME.success} name="이자 수익" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </Paper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Box>
    );
};

export default CashAssets;
