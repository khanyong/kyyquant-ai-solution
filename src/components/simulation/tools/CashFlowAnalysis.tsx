import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { AccountBalance, CompareArrows } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    success: '#2CB67D',
    border: '#2A2F3A'
};

const CashFlowAnalysis: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <CompareArrows sx={{ fontSize: 36, color: THEME.success }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">현금 흐름 분석</Typography>
                    <Typography variant="body1" color={THEME.textDim}>월간 수입과 지출을 분석하여 잉여 현금 흐름을 파악합니다.</Typography>
                </Box>
            </Box>

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}` }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>수입 (Income)</Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography color={THEME.textDim}>근로 소득</Typography>
                                <Typography>₩4,500,000</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography color={THEME.textDim}>기타 소득</Typography>
                                <Typography>₩200,000</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}` }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>지출 (Expenses)</Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography color={THEME.textDim}>고정 지출</Typography>
                                <Typography>₩1,200,000</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography color={THEME.textDim}>변동 지출</Typography>
                                <Typography>₩800,000</Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color={THEME.textDim}>월 잉여 현금 (Monthly Surplus)</Typography>
                        <Typography variant="h3" fontWeight="bold" color={THEME.success} sx={{ mt: 1 }}>
                            + ₩2,700,000
                        </Typography>
                        <Typography variant="body2" color={THEME.textDim} sx={{ mt: 2 }}>
                            이 자금을 투자 포트폴리오에 배분하여 자산을 증식할 수 있습니다.
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default CashFlowAnalysis;
