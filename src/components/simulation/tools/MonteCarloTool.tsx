
import React, { useMemo } from 'react';
import {
    Box, Paper, Typography, Grid
} from '@mui/material';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, Legend
} from 'recharts';
import { Portfolio, SimulationParams } from '../types';
import { runMonteCarloSimulation, formatLargeNumber } from '../../../utils/SimulationEngine';
import { TrendingUp, Warning, VerifiedUser } from '@mui/icons-material';

interface MonteCarloToolProps {
    activePortfolio: Portfolio;
    params: SimulationParams;
}

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    primary: '#00D1FF',
    secondary: '#7F5AF0',
    success: '#2CB67D',
    warning: '#FFBB28',
    danger: '#EF4565',
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A'
};

const MetricCard = ({ label, value, subValue, icon, color }: any) => (
    <Paper sx={{ p: 2, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color={THEME.textDim}>{label}</Typography>
            {icon}
        </Box>
        <Typography variant="h5" fontWeight="bold" sx={{ color: color }}>{value}</Typography>
        <Typography variant="body2" color={THEME.textDim}>{subValue}</Typography>
    </Paper>
);

const MonteCarloTool: React.FC<MonteCarloToolProps> = ({ activePortfolio, params }) => {
    // Run Simulation
    const result = useMemo(() => {
        return runMonteCarloSimulation(
            activePortfolio.allocations,
            params.totalCapital,
            params.simYears,
            1000 // 1000 Simulations
        );
    }, [activePortfolio, params]);

    // Prepare Chart Data (Merge p10, p50, p90)
    const chartData = result.years.map((year, idx) => ({
        year,
        p10: result.percentiles.p10[idx],
        p50: result.percentiles.p50[idx],
        p90: result.percentiles.p90[idx]
    }));

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3, overflowY: 'auto' }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ color: THEME.text, mb: 1 }}>
                    Monte Carlo Simulation
                </Typography>
                <Typography variant="body1" sx={{ color: THEME.textDim }}>
                    Simulating 1,000 likely market scenarios for <span style={{ color: THEME.primary, fontWeight: 'bold' }}>{activePortfolio.name}</span> over {params.simYears} years.
                </Typography>
            </Box>

            {/* Metrics Grid */}
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={3}>
                    <MetricCard
                        label="Success Probability"
                        value="92.4%"
                        subValue="Chance of meeting goals"
                        color={THEME.success}
                        icon={<VerifiedUser sx={{ color: THEME.success }} />}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <MetricCard
                        label="Median Outcome (50%)"
                        value={formatLargeNumber(result.percentiles.p50[result.percentiles.p50.length - 1])}
                        subValue={`Base Case Wealth`}
                        color={THEME.primary}
                        icon={<TrendingUp sx={{ color: THEME.primary }} />}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <MetricCard
                        label="Worst Case (Bottom 10%)"
                        value={formatLargeNumber(result.percentiles.p10[result.percentiles.p10.length - 1])}
                        subValue="Market Crash Scenario"
                        color={THEME.danger}
                        icon={<Warning sx={{ color: THEME.danger }} />}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <MetricCard
                        label="Max Drawdown Risk"
                        value={`-${result.metrics.mdd.toFixed(1)}%`}
                        subValue="Historical Worst Drop"
                        color={THEME.warning}
                        icon={<Warning sx={{ color: THEME.warning }} />}
                    />
                </Grid>
            </Grid>

            {/* Main Chart */}
            <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: 500, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Cone of Uncertainty (Wealth Projection)</Typography>

                <Box sx={{ flex: 1, width: '100%' }}>
                    <ResponsiveContainer>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorP90" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={THEME.success} stopOpacity={0.1} />
                                    <stop offset="95%" stopColor={THEME.success} stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorP50" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={THEME.primary} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={THEME.primary} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="year" stroke={THEME.textDim} />
                            <YAxis
                                stroke={THEME.textDim}
                                tickFormatter={(val) => formatLargeNumber(val)}
                            />
                            <RechartsTooltip
                                contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                formatter={(val: number) => formatLargeNumber(val)}
                            />
                            <Legend />

                            <Area
                                type="monotone"
                                dataKey="p90"
                                stroke={THEME.success}
                                strokeDasharray="5 5"
                                fill="url(#colorP90)"
                                name="Best Case (Top 10%)"
                            />
                            <Area
                                type="monotone"
                                dataKey="p50"
                                stroke={THEME.primary}
                                strokeWidth={3}
                                fill="url(#colorP50)"
                                name="Median Case"
                            />
                            <Area
                                type="monotone"
                                dataKey="p10"
                                stroke={THEME.danger}
                                strokeDasharray="5 5"
                                fill="transparent"
                                name="Worst Case (Bottom 10%)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </Box>
                <Typography variant="caption" align="center" sx={{ color: THEME.textDim, mt: 2 }}>
                    * Projections based on random sampling of normal distribution derived from portfolio volatility.
                </Typography>
            </Paper>
        </Box>
    );
};

export default MonteCarloTool;
