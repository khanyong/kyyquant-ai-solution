
import React, { useState } from 'react';
import { Box, Paper, TextField, Button, Typography } from '@mui/material';
import { LockOutlined } from '@mui/icons-material';

import IPCSidebar from './IPCSidebar';
import IPCHome from './IPCHome';
import PortfolioBacktest from './tools/PortfolioBacktest';

// Placeholder for future tools
const MonteCarloPlaceholder = () => <Box sx={{ p: 4, color: '#fff' }}>Monte Carlo Simulation under construction.</Box>;
const FactorPlaceholder = () => <Box sx={{ p: 4, color: '#fff' }}>Factor Analysis under construction.</Box>;

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    text: '#E0E6ED',
    border: '#2A2F3A',
    primary: '#00D1FF'
};

const VisualRetirementPlanner: React.FC = () => {
    // --- Auth State ---
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [authError, setAuthError] = useState(false);

    // --- Navigation State ---
    const [activeTool, setActiveTool] = useState('dashboard');

    const handleLogin = () => {
        if (password === '805500') {
            setIsAuthenticated(true);
            setAuthError(false);
        } else {
            setAuthError(true);
        }
    };

    // --- Render: Security Gate ---
    if (!isAuthenticated) return (
        <Box sx={{ height: '100vh', bgcolor: THEME.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Paper elevation={0} sx={{ p: 5, maxWidth: 400, textAlign: 'center', borderRadius: 4, bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                <LockOutlined sx={{ fontSize: 40, color: THEME.primary, mb: 2 }} />
                <Typography variant="h5" fontWeight="bold" sx={{ color: THEME.text, mb: 1 }}>IPC Security</Typography>
                <Typography variant="body2" sx={{ color: '#94A1B2', mb: 4 }}>
                    Authorized Personnel Only.<br />Enter Default PIN: 805500
                </Typography>
                <TextField
                    fullWidth autoFocus type="password"
                    variant="outlined"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    error={authError}
                    onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                    sx={{ mb: 3, input: { color: THEME.text }, fieldset: { borderColor: THEME.border } }}
                />
                <Button fullWidth variant="contained" size="large" onClick={handleLogin} sx={{ bgcolor: THEME.primary, color: '#000', fontWeight: 'bold' }}>
                    ACCESS TERMINAL
                </Button>
            </Paper>
        </Box>
    );

    // --- Render: IPC Shell ---
    return (
        <Box sx={{ display: 'flex', height: '100vh', bgcolor: THEME.bg, color: THEME.text }}>
            {/* Sidebar */}
            <IPCSidebar activeTool={activeTool} setActiveTool={setActiveTool} />

            {/* Main Content Area */}
            <Box sx={{ flex: 1, height: '100%', overflow: 'hidden', p: 0 }}>
                {activeTool === 'dashboard' && <IPCHome onNavigate={setActiveTool} />}
                {activeTool === 'backtest' && <PortfolioBacktest />}
                {activeTool === 'montecarlo' && <MonteCarloPlaceholder />}
                {activeTool === 'factor' && <FactorPlaceholder />}
            </Box>
        </Box>
    );
};

export default VisualRetirementPlanner;
