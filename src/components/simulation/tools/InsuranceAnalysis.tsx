import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import { HealthAndSafety, Shield } from '@mui/icons-material';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    border: 'var(--ipc-border)'
};

const InsuranceAnalysis: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Shield sx={{ fontSize: 36, color: THEME.primary }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">보험 및 리스크 관리</Typography>
                    <Typography variant="body1" color={THEME.textDim}>가입된 보험 내역을 확인하고 보장 범위를 분석합니다.</Typography>
                </Box>
            </Box>

            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box sx={{ textAlign: 'center', color: THEME.textDim }}>
                    <HealthAndSafety sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
                    <Typography variant="h6">보험 보장 분석</Typography>
                    <Typography variant="body2">생명, 실손, 암 보험 등 주요 보장 내용을 시각화하여 제공할 예정입니다.</Typography>
                </Box>
            </Paper>
        </Box>
    );
};

export default InsuranceAnalysis;
