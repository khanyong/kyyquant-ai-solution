import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import { Flag, EventNote } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    secondary: '#7F5AF0',
    border: '#2A2F3A'
};

const LifeGoalPlanning: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Flag sx={{ fontSize: 36, color: THEME.secondary }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">생애 재무 목표 (Life Goals)</Typography>
                    <Typography variant="body1" color={THEME.textDim}>결혼, 주택 마련, 자녀 교육 등 주요 생애 이벤트 자금을 계획합니다.</Typography>
                </Box>
            </Box>

            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box sx={{ textAlign: 'center', color: THEME.textDim }}>
                    <EventNote sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
                    <Typography variant="h6">목표 기반 투자 (Goal Based Investing)</Typography>
                    <Typography variant="body2">타임라인에 따른 자금 필요액과 달성 가능성을 시뮬레이션 합니다.</Typography>
                </Box>
            </Paper>
        </Box>
    );
};

export default LifeGoalPlanning;
