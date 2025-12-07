
import React from 'react';
import { Box, Paper, Typography, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import {
    ShowChart, PieChart, BarChart, Rule, Calculate,
    TrendingUp, Assignment, Settings, Dashboard
} from '@mui/icons-material';

const THEME = {
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    primary: '#00D1FF',
    hover: '#1E232F'
};

interface IPCSidebarProps {
    activeTool: string;
    setActiveTool: (tool: string) => void;
}

const MENU_ITEMS = [
    {
        category: "General",
        items: [
            { id: 'dashboard', label: 'Dashboard', icon: <Dashboard /> }
        ]
    },
    {
        category: "Portfolio Analysis",
        items: [
            { id: 'backtest', label: 'Backtest Portfolio', icon: <ShowChart /> },
            { id: 'factor', label: 'Factor Analysis', icon: <BarChart /> },
            { id: 'allocation', label: 'Asset Allocation', icon: <PieChart /> }
        ]
    },
    {
        category: "Financial Planning",
        items: [
            { id: 'montecarlo', label: 'Monte Carlo Sim', icon: <TrendingUp /> },
            { id: 'goals', label: 'Financial Goals', icon: <Rule /> }
        ]
    }
];

const IPCSidebar: React.FC<IPCSidebarProps> = ({ activeTool, setActiveTool }) => {
    return (
        <Paper
            sx={{
                width: 260,
                height: '100%',
                bgcolor: THEME.panel,
                display: 'flex',
                flexDirection: 'column',
                borderRight: '1px solid #2A2F3A',
                borderRadius: 0
            }}
            elevation={0}
        >
            <Box sx={{ p: 2, borderBottom: '1px solid #2A2F3A' }}>
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
                                        '&.Mui-selected': { bgcolor: 'rgba(0, 209, 255, 0.1)', borderRight: `3px solid ${THEME.primary}` },
                                        '&:hover': { bgcolor: THEME.hover }
                                    }}
                                >
                                    <ListItemIcon sx={{ color: activeTool === item.id ? THEME.primary : THEME.textDim, minWidth: 40 }}>
                                        {item.icon}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.label}
                                        primaryTypographyProps={{
                                            variant: 'body2',
                                            color: activeTool === item.id ? THEME.primary : THEME.text
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
