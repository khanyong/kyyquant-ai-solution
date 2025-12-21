import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Paper, Typography, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, IconButton } from '@mui/material';
import {
    ShowChart, PieChart, BarChart, Rule, Calculate,
    TrendingUp, Assignment, Settings, Dashboard, ArrowBack, VerifiedUser,
    AccountBalanceWallet, MoneyOff, HomeWork, Category, CompareArrows, Shield, Flag
} from '@mui/icons-material';

const THEME = {
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    hover: 'var(--ipc-bg-hover)'
};

interface IPCSidebarProps {
    activeTool: string;
    setActiveTool: (tool: string) => void;
}

const MENU_ITEMS = [
    {
        category: "투자/자산관리",
        items: [
            { id: 'dashboard', labelKo: '개인자산', labelEn: 'My Assets', icon: <Dashboard /> },
            { id: 'backtest', labelKo: '포트폴리오', labelEn: 'Portfolio', icon: <ShowChart /> },
            { id: 'allocation', labelKo: '상품', labelEn: 'Financial Products', icon: <PieChart /> },
            { id: 'factor', labelKo: '투자정보', labelEn: 'Investment Info', icon: <BarChart /> },
            { id: 'montecarlo', labelKo: '로보어드바이저', labelEn: 'Robo-Advisor', icon: <TrendingUp /> },
            { id: 'isa', labelKo: 'ISA', labelEn: 'ISA', icon: <Rule /> },
            { id: 'pension', labelKo: '퇴직연금', labelEn: 'Retirement Pension', icon: <Assignment /> },
            { id: 'market_guide', labelKo: '시장가이드', labelEn: 'Market Guide', icon: <TrendingUp /> }
        ]
    },
    {
        category: "자산/부채 관리",
        items: [
            { id: 'cash_assets', labelKo: '현금/예적금', labelEn: 'Cash & Deposits', icon: <AccountBalanceWallet /> },
            { id: 'real_estate', labelKo: '부동산', labelEn: 'Real Estate', icon: <HomeWork /> },
            { id: 'other_assets', labelKo: '기타/대체자산', labelEn: 'Other Assets', icon: <Category /> },
            { id: 'debt_mgmt', labelKo: '부채 관리', labelEn: 'Debt Mgmt', icon: <MoneyOff /> }
        ]
    },
    {
        category: "생애/리스크 설계",
        items: [
            { id: 'cashflow', labelKo: '현금흐름표', labelEn: 'Cash Flow', icon: <CompareArrows /> },
            { id: 'insurance', labelKo: '보험/리스크', labelEn: 'Insurance', icon: <Shield /> },
            { id: 'goals', labelKo: '재무목표', labelEn: 'Life Goals', icon: <Flag /> }
        ]
    },
    {
        category: "설정",
        items: [
            { id: 'settings', labelKo: '환경설정', labelEn: 'Settings', icon: <Settings /> }
        ]
    }
];

const IPCSidebar: React.FC<IPCSidebarProps> = ({ activeTool, setActiveTool }) => {
    const navigate = useNavigate();

    return (
        <Paper
            sx={{
                width: 260,
                height: '100%',
                bgcolor: THEME.panel,
                display: 'flex',
                flexDirection: 'column',
                borderRight: '1px solid #e0e0e0',
                borderRadius: 0
            }}
            elevation={0}
        >
            <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h6" fontWeight="900" sx={{ letterSpacing: 1, color: THEME.text }}>
                    IPC <span style={{ color: THEME.primary, fontWeight: 400 }}>Terminal</span>
                </Typography>
            </Box>

            <List sx={{ flex: 1, overflowY: 'auto' }}>
                {MENU_ITEMS.map((cat) => (
                    <Box key={cat.category} sx={{ mb: 2 }}>
                        <Typography variant="overline" sx={{ px: 2, color: THEME.textDim, fontWeight: 'bold' }}>
                            {cat.category}
                        </Typography>
                        {cat.items.map((item) => (
                            <ListItem key={item.id} disablePadding>
                                <ListItemButton
                                    selected={activeTool === item.id}
                                    onClick={() => setActiveTool(item.id)}
                                    sx={{
                                        '&.Mui-selected': { bgcolor: 'var(--ipc-primary-light)', borderRight: `3px solid ${THEME.primary}` },
                                        '&:hover': { bgcolor: THEME.hover }
                                    }}
                                >
                                    <ListItemIcon sx={{ color: activeTool === item.id ? THEME.primary : THEME.textDim, minWidth: 40 }}>
                                        {item.icon}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={
                                            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.8 }}>
                                                <span>{item.labelKo}</span>
                                                <Typography variant="caption" sx={{ fontSize: '0.65rem', color: activeTool === item.id ? THEME.primary : THEME.textDim, opacity: 0.8 }}>
                                                    {item.labelEn}
                                                </Typography>
                                            </Box>
                                        }
                                        primaryTypographyProps={{
                                            variant: 'body2',
                                            color: activeTool === item.id ? THEME.primary : THEME.text,
                                            fontWeight: 500
                                        }}
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </Box>
                ))}
            </List>

            <Box sx={{ p: 2, borderTop: '1px solid #2A2F3A' }}>
                <Typography variant="caption" color={THEME.textDim}>
                    v2.0.0 Expert Build<br />
                    Connected: Localhost
                </Typography>
            </Box>
        </Paper>
    );
};

export default IPCSidebar;
