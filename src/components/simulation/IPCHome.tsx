
import React from 'react';
import { Box, Paper, Typography, Grid, Card, CardActionArea, Divider } from '@mui/material';
import { ShowChart, BarChart, TrendingUp, PieChart, ArrowForward, AccessTime } from '@mui/icons-material';

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    primary: 'var(--ipc-primary)',
    secondary: 'var(--ipc-secondary)',
    success: 'var(--ipc-success)',
    border: 'var(--ipc-border)'
};

interface IPCHomeProps {
    setActiveTool: (tool: string) => void;
}

const TOOLS = [
    {
        id: 'backtest',
        title: 'Backtest Portfolio',
        desc: 'Test portfolio asset allocation based on historical returns.',
        icon: <ShowChart sx={{ fontSize: 40, color: THEME.primary }} />,
        tag: 'Most Popular'
    },
    {
        id: 'montecarlo',
        title: 'Monte Carlo Simulation',
        desc: 'Run Monte Carlo simulations to test long term expected portfolio growth and survival.',
        icon: <TrendingUp sx={{ fontSize: 40, color: 'var(--ipc-success)' }} />,
        tag: 'Planning'
    },
    {
        id: 'allocation',
        title: 'Portfolio Optimization',
        desc: 'Chart the efficient frontier to explore risk vs. return trade-offs.',
        icon: <PieChart sx={{ fontSize: 40, color: THEME.secondary }} />,
        tag: 'Optimization'
    },
    {
        id: 'factor',
        title: 'Factor Analysis',
        desc: 'Analyze the sources of risk and return of manager returns.',
        icon: <BarChart sx={{ fontSize: 40, color: 'var(--ipc-warning)' }} />,
        tag: 'Research'
    }
];

const IPCHome: React.FC<IPCHomeProps> = ({ setActiveTool }) => {
    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto', height: '100%', overflowY: 'auto' }}>
            {/* Header Section */}
            <Box sx={{ mb: 6, textAlign: 'center' }}>
                <Typography variant="h3" className="ipc-header-text" sx={{ mb: 2, color: THEME.text }}>
                    IPC <span style={{ fontStyle: 'italic', fontFamily: 'Lora, serif' }}>Insight</span>
                </Typography>
                <Typography variant="h6" className="ipc-sub-text" sx={{ maxWidth: 700, mx: 'auto' }}>
                    Quantitative investment analysis tools for portfolio construction, backtesting, and risk management. No login required for standard features.
                </Typography>
                <Box className="ipc-section-divider" sx={{ mt: 4, width: '60px', mx: 'auto', borderBottomColor: THEME.primary }} />
            </Box>

            {/* Tools Grid */}
            <Grid container spacing={3}>
                {TOOLS.map((tool) => (
                    <Grid item xs={12} sm={6} md={6} key={tool.id}>
                        <Card sx={{ bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: '100%' }}>
                            <CardActionArea
                                onClick={() => setActiveTool(tool.id)}
                                sx={{ height: '100%', p: 3, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start' }}
                            >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 2 }}>
                                    {tool.icon}
                                    <Paper sx={{ px: 1, py: 0.5, bgcolor: 'var(--ipc-bg-subtle)', borderRadius: 1 }}>
                                        <Typography variant="caption" sx={{ color: THEME.textDim, fontWeight: 'bold' }}>
                                            {tool.tag}
                                        </Typography>
                                    </Paper>
                                </Box>
                                <Typography variant="h5" className="ipc-header-text" sx={{ mb: 1.5, color: THEME.text }}>
                                    {tool.title}
                                </Typography>
                                <Typography variant="body1" className="ipc-sub-text" sx={{ mb: 3, flex: 1 }}>
                                    {tool.desc}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', color: THEME.primary, gap: 1 }}>
                                    <Typography variant="button" fontWeight="bold">Open Analysis</Typography>
                                    <ArrowForward fontSize="small" />
                                </Box>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Divider sx={{ my: 6, borderColor: THEME.border }} />

            {/* Quick Links / Footerish */}
            <Grid container spacing={4}>
                <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
                        <AccessTime sx={{ color: THEME.textDim }} />
                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>Recent Updates</Typography>
                    </Box>
                    <Typography variant="body2" color={THEME.textDim}>
                        Added Factor Analysis tool for deeper risk decomposition.
                    </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
                        <TrendingUp sx={{ color: THEME.textDim }} />
                        <Typography variant="h6" fontWeight="bold" color={THEME.text}>Market Data</Typography>
                    </Box>
                    <Typography variant="body2" color={THEME.textDim}>
                        Data updated as of {new Date().toLocaleDateString()}.
                    </Typography>
                </Grid>
            </Grid>
        </Box>
    );
};

export default IPCHome;
