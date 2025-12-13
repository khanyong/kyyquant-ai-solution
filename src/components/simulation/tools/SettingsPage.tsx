import React from 'react';
import { Box, Typography, Paper, Switch, List, ListItem, ListItemText, ListItemSecondaryAction, Divider } from '@mui/material';
import { Settings } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A'
};

const SettingsPage: React.FC = () => {
    return (
        <Box sx={{ p: 4, maxWidth: 800, margin: '0 auto', color: THEME.text }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Settings sx={{ fontSize: 36, color: THEME.text }} />
                <Typography variant="h4" fontWeight="bold">환경 설정</Typography>
            </Box>

            <Paper sx={{ bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 2 }}>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="다크 모드"
                            secondary="어두운 테마를 항상 유지합니다."
                            primaryTypographyProps={{ fontWeight: 'bold' }}
                            secondaryTypographyProps={{ color: THEME.textDim }}
                        />
                        <ListItemSecondaryAction>
                            <Switch edge="end" checked={true} />
                        </ListItemSecondaryAction>
                    </ListItem>
                    <Divider sx={{ borderColor: THEME.border }} />
                    <ListItem>
                        <ListItemText
                            primary="알림 설정"
                            secondary="중요한 시장 변화나 목표 달성 시 알림을 받습니다."
                            primaryTypographyProps={{ fontWeight: 'bold' }}
                            secondaryTypographyProps={{ color: THEME.textDim }}
                        />
                        <ListItemSecondaryAction>
                            <Switch edge="end" checked={true} />
                        </ListItemSecondaryAction>
                    </ListItem>
                    <Divider sx={{ borderColor: THEME.border }} />
                    <ListItem>
                        <ListItemText
                            primary="시뮬레이션 데이터 초기화"
                            secondary="저장된 모든 포트폴리오와 가정치를 초기화합니다."
                            primaryTypographyProps={{ fontWeight: 'bold', color: '#EF4565' }}
                            secondaryTypographyProps={{ color: THEME.textDim }}
                        />
                    </ListItem>
                </List>
            </Paper>

            <Box sx={{ mt: 4, textAlign: 'center', color: THEME.textDim }}>
                <Typography variant="caption">IPC Terminal v2.0.0</Typography>
            </Box>
        </Box>
    );
};

export default SettingsPage;
