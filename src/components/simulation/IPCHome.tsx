
import React from 'react';
import { Box, Typography, Grid, Paper, CardActionArea } from '@mui/material';
import { ShowChart, TrendingUp, ScatterPlot, Tune } from '@mui/icons-material';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    primary: '#00D1FF',
    border: '#2A2F3A'
};

interface ToolCardProps {
    title: string;
    desc: string;
    icon: React.ReactNode;
    onClick: () => void;
}

const ToolCard: React.FC<ToolCardProps> = ({ title, desc, icon, onClick }) => (
    <Paper
        sx={{
            height: '100%',
            bgcolor: THEME.panel,
            border: '1px solid ' + THEME.border,
            transition: '0.2s',
            '&:hover': { borderColor: THEME.primary, transform: 'translateY(-2px)' }
        }}
    >
        <CardActionArea onClick={onClick} sx={{ height: '100%', p: 3, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start' }}>
            <Box sx={{ p: 1, bgcolor: 'rgba(0, 209, 255, 0.1)', borderRadius: 2, mb: 2, color: THEME.primary }}>
                {icon}
            </Box>
            <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ color: THEME.text }}>
                {title}
            </Typography>
            <Typography variant="body2" sx={{ color: THEME.textDim }}>
                {desc}
            </Typography>
        </CardActionArea>
    </Paper>
);

interface IPCHomeProps {
    onNavigate: (toolId: string) => void;
}

const IPCHome: React.FC<IPCHomeProps> = ({ onNavigate }) => {
    return (
        <Box sx={{ p: 4, height: '100%', overflowY: 'auto' }}>
            <Typography variant="h4" fontWeight="bold" sx={{ color: THEME.text, mb: 1 }}>
                Welcome to IPC Terminal
            </Typography>
            <Typography variant="body1" sx={{ color: THEME.textDim, mb: 4 }}>
                Select a tool to begin your quantitative analysis.
            </Typography>

            <Typography variant="h6" sx={{ color: THEME.primary, mb: 2, fontWeight: 'bold' }}>
                Simulation & Analysis
            </Typography>
            <Grid container spacing={3} sx={{ mb: 5 }}>
                <Grid item xs={12} sm={6} md={4}>
                    <ToolCard
                        title="Backtest Portfolio"
                        desc="Analyze portfolio asset allocation strategies based on statistical profiles."
                        icon={<ShowChart fontSize="large" />}
                        onClick={() => onNavigate('backtest')}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <ToolCard
                        title="Monte Carlo Simulation"
                        desc="Run 10,000+ scenarios to test portfolio survival probabilities."
                        icon={<TrendingUp fontSize="large" />}
                        onClick={() => onNavigate('montecarlo')}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <ToolCard
                        title="Factor Analysis"
                        desc="Evaluate exposure to Fama-French factors and risk premiums."
                        icon={<ScatterPlot fontSize="large" />}
                        onClick={() => onNavigate('factor')}
                    />
                </Grid>
            </Grid>

            <Typography variant="h6" sx={{ color: THEME.primary, mb: 2, fontWeight: 'bold' }}>
                Optimization
            </Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={4}>
                    <ToolCard
                        title="Efficient Frontier"
                        desc="Find the optimal portfolio mix for a given risk level."
                        icon={<Tune fontSize="large" />}
                        onClick={() => onNavigate('allocation')}
                    />
                </Grid>
            </Grid>
        </Box>
    );
};

export default IPCHome;
