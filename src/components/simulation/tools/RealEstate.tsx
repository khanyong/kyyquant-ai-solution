import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { HomeWork, Domain } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    primary: '#00D1FF',
    border: '#2A2F3A'
};

const RealEstate: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <HomeWork sx={{ fontSize: 36, color: THEME.primary }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">부동산 자산 관리</Typography>
                    <Typography variant="body1" color={THEME.textDim}>보유 부동산의 가치 변동과 임대 수익을 관리합니다.</Typography>
                </Box>
            </Box>

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Box sx={{ textAlign: 'center', color: THEME.textDim }}>
                            <Domain sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
                            <Typography variant="h6">등록된 부동산이 없습니다.</Typography>
                            <Typography variant="body2">거주 주택이나 투자용 부동산을 추가하여 자산 포트폴리오를 완성하세요.</Typography>
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}` }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>부동산 시장 동향</Typography>
                            <Typography variant="body2" color={THEME.textDim}>
                                최신 부동산 시장 데이터와 전망을 제공할 예정입니다.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default RealEstate;
