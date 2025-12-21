
import React from 'react';
import {
    Box, Paper, Typography, Grid, TextField,
    MenuItem, Select, FormControl, InputLabel, InputAdornment
} from '@mui/material';

const THEME = {
    panel: 'var(--ipc-bg-panel)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    border: 'var(--ipc-border)',
    primary: 'var(--ipc-primary)'
};

interface PortfolioSettingsProps {
    years: number;
    setYears: (v: number) => void;
    monthlyContribution: number;
    setMonthlyContribution: (v: number) => void;
    rebalanceFreq: string;
    setRebalanceFreq: (v: string) => void;
    benchmark: string;
    setBenchmark: (v: string) => void;
}

const PortfolioSettings: React.FC<PortfolioSettingsProps> = ({
    years, setYears,
    monthlyContribution, setMonthlyContribution,
    rebalanceFreq, setRebalanceFreq,
    benchmark, setBenchmark
}) => {
    return (
        <Paper sx={{ p: 2, mb: 2, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2 }}>
            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: THEME.text }}>
                Portfolio Analysis Parameters
            </Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                    <TextField
                        label="Time Period (Years)"
                        type="number"
                        fullWidth
                        size="small"
                        value={years}
                        onChange={(e) => setYears(Number(e.target.value))}
                        sx={{
                            input: { color: THEME.text },
                            label: { color: THEME.textDim },
                            fieldset: { borderColor: THEME.border }
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <TextField
                        label="Monthly Contribution"
                        type="number"
                        fullWidth
                        size="small"
                        value={monthlyContribution}
                        onChange={(e) => setMonthlyContribution(Number(e.target.value))}
                        InputProps={{
                            startAdornment: <InputAdornment position="start"><span style={{ color: THEME.textDim }}>₩</span></InputAdornment>,
                        }}
                        sx={{
                            input: { color: THEME.text },
                            label: { color: THEME.textDim },
                            fieldset: { borderColor: THEME.border }
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                        <InputLabel sx={{ color: THEME.textDim }}>Rebalancing</InputLabel>
                        <Select
                            value={rebalanceFreq}
                            label="Rebalancing"
                            onChange={(e) => setRebalanceFreq(e.target.value)}
                            sx={{
                                color: THEME.text,
                                '.MuiOutlinedInput-notchedOutline': { borderColor: THEME.border },
                                '.MuiSvgIcon-root': { color: THEME.textDim }
                            }}
                        >
                            <MenuItem value="No Rebalancing">No Rebalancing</MenuItem>
                            <MenuItem value="Annually">Annually</MenuItem>
                            <MenuItem value="Semi-Annually">Semi-Annually</MenuItem>
                            <MenuItem value="Quarterly">Quarterly</MenuItem>
                            <MenuItem value="Monthly">Monthly</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                        <InputLabel sx={{ color: THEME.textDim }}>Benchmark</InputLabel>
                        <Select
                            value={benchmark}
                            label="Benchmark"
                            onChange={(e) => setBenchmark(e.target.value)}
                            sx={{
                                color: THEME.text,
                                '.MuiOutlinedInput-notchedOutline': { borderColor: THEME.border },
                                '.MuiSvgIcon-root': { color: THEME.textDim }
                            }}
                        >
                            <MenuItem value="SPY">S&P 500 (SPY)</MenuItem>
                            <MenuItem value="6040">60/40 Portfolio</MenuItem>
                            <MenuItem value="CASH">Cash (Risk Free)</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>
        </Paper>
    );
};

export default PortfolioSettings;
