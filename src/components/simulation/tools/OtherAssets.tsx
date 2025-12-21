import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import { Diamond, Category } from '@mui/icons-material';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    warning: 'var(--ipc-warning)',
    border: 'var(--ipc-border)'
};

const OtherAssets: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Category sx={{ fontSize: 36, color: THEME.warning }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">기타 실물 자산</Typography>
                    <Typography variant="body1" color={THEME.textDim}>금, 가상화폐, 미술품, 회원권 등 대체 자산을 관리합니다.</Typography>
                </Box>
            </Box>

            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box sx={{ textAlign: 'center', color: THEME.textDim }}>
                    <Diamond sx={{ fontSize: 60, opacity: 0.5, mb: 2 }} />
                    <Typography variant="h6">대체 자산 포트폴리오</Typography>
                    <Typography variant="body2">다양한 실물 자산을 등록하여 전체 순자산을 파악하세요.</Typography>
                </Box>
            </Paper>
        </Box>
    );
};

export default OtherAssets;
