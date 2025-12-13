
import React, { useMemo } from 'react';
import {
    Box, Paper, Typography, Grid, Chip
} from '@mui/material';
import {
    ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, ReferenceLine, LabelList
} from 'recharts';
import { Portfolio } from '../types';
import { AutoGraph, Lightbulb, CheckCircle } from '@mui/icons-material';

interface OptimizationToolProps {
    activePortfolio: Portfolio;
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

const OptimizationTool: React.FC<OptimizationToolProps> = ({ activePortfolio }) => {

    // 1. Calculate Current Metrics
    const currentMetrics = useMemo(() => {
        let weightedReturn = 0;
        let weightedVol = 0;
        let totalWeight = 0;

        activePortfolio.allocations.forEach(alloc => {
            totalWeight += alloc.amount;
            weightedReturn += (alloc.asset.expectedReturn / 100) * alloc.amount;
            weightedVol += ((alloc.asset.volatility || 15) / 100) * alloc.amount;
        });

        if (totalWeight === 0) return { x: 5, y: 5 };

        // Diversification Bonus (Simulated)
        if (activePortfolio.allocations.length > 2) weightedVol *= 0.85;

        return {
            x: (weightedVol / totalWeight) * 100, // Volatility %
            y: (weightedReturn / totalWeight) * 100 // Return %
        };
    }, [activePortfolio]);

    // 2. Simulate Efficient Frontier (Random Portfolios)
    const frontierData = useMemo(() => {
        const data = [];
        if (activePortfolio.allocations.length < 2) return [];

        for (let i = 0; i < 300; i++) {
            // Random weights
            const weights = activePortfolio.allocations.map(() => Math.random());
            const sumWeights = weights.reduce((a, b) => a + b, 0);

            let simReturn = 0;
            let simVol = 0;

            activePortfolio.allocations.forEach((alloc, idx) => {
                const w = weights[idx] / sumWeights;
                simReturn += (alloc.asset.expectedReturn) * w;
                simVol += (alloc.asset.volatility || 15) * w;
            });

            // Diversification bonus
            simVol *= 0.85;

            data.push({ x: simVol, y: simReturn });
        }
        return data;
    }, [activePortfolio]);

    const isOptimal = currentMetrics.y > 7 && currentMetrics.x < 15; // Mock Logic

    if (activePortfolio.allocations.length < 2) {
        return (
            <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 2 }}>
                <AutoGraph sx={{ fontSize: 60, color: THEME.textDim }} />
                <Typography variant="h6" color={THEME.textDim}>
                    Add at least 2 assets to run optimization.
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3, overflowY: 'auto' }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ color: THEME.text, mb: 1 }}>
                    Asset Allocation
                </Typography>
                <Typography variant="body1" sx={{ color: THEME.textDim }}>
                    Efficient Frontier Analysis for <span style={{ color: THEME.primary, fontWeight: 'bold' }}>{activePortfolio.name}</span>.
                </Typography>
            </Box>

            <Grid container spacing={3} sx={{ height: '100%' }}>
                {/* Left: Chart */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 4, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: 500 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Risk vs Return Profile</Typography>
                        <ResponsiveContainer width="100%" height="90%">
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis
                                    type="number" dataKey="x" name="Risk (Vol)" unit="%"
                                    stroke={THEME.textDim} domain={['auto', 'auto']}
                                    label={{ value: 'Risk (Standard Deviation)', position: 'insideBottom', offset: -10, fill: THEME.textDim }}
                                />
                                <YAxis
                                    type="number" dataKey="y" name="Return" unit="%"
                                    stroke={THEME.textDim} domain={['auto', 'auto']}
                                    label={{ value: 'Expected Return', angle: -90, position: 'insideLeft', fill: THEME.textDim }}
                                />
                                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }} />

                                {/* Simulated Portfolios */}
                                <Scatter name="Potential Portfolios" data={frontierData} fill="#8884d8" fillOpacity={0.5} shape="circle" />

                                {/* Current Portfolio */}
                                <Scatter name="Current" data={[currentMetrics]} fill={THEME.primary} shape="star" z={200}>
                                    <LabelList dataKey="x" content={() => null} />
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Right: Recommendation */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, background: 'linear-gradient(180deg, rgba(44, 182, 125, 0.1) 0%, rgba(21, 25, 33, 0) 100%)' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                <Lightbulb sx={{ color: THEME.success }} />
                                <Typography variant="h6" fontWeight="bold">AI Insight</Typography>
                            </Box>
                            <Typography variant="body1" sx={{ color: THEME.text, mb: 2 }}>
                                Your portfolio lies {isOptimal ? 'ON' : 'BELOW'} the efficient frontier.
                            </Typography>

                            {!isOptimal && (
                                <>
                                    <Typography variant="body2" sx={{ color: THEME.textDim, mb: 2 }}>
                                        You are taking <b>{(currentMetrics.x).toFixed(1)}%</b> risk for a <b>{(currentMetrics.y).toFixed(1)}%</b> return.
                                        Analysis suggests you could increase return to <b>{(currentMetrics.y * 1.2).toFixed(1)}%</b> with the same risk level by optimizing weights.
                                    </Typography>
                                    <Chip icon={<AutoGraph />} label="Auto-Optimize Available" color="primary" variant="outlined" clickable />
                                </>
                            )}

                            {isOptimal && (
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: THEME.success }}>
                                    <CheckCircle fontSize="small" />
                                    <Typography variant="body2" fontWeight="bold">Portfolio is Efficient</Typography>
                                </Box>
                            )}
                        </Paper>

                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border }}>
                            <Typography variant="subtitle2" color={THEME.textDim} sx={{ mb: 1 }}>Current Metrics</Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="h4" fontWeight="bold" color={THEME.primary}>{currentMetrics.y.toFixed(1)}%</Typography>
                                    <Typography variant="caption" color={THEME.textDim}>Return</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="h4" fontWeight="bold" color={THEME.warning}>{currentMetrics.x.toFixed(1)}%</Typography>
                                    <Typography variant="caption" color={THEME.textDim}>Risk (Vol)</Typography>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default OptimizationTool;
