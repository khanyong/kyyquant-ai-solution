
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
    bg: '#FFFFFF',
    panel: '#FFFFFF',
    primary: '#121212', // Editorial Black
    secondary: '#757575',
    success: '#C5A065', // Journalistic Gold
    warning: '#D32F2F', // Editorial Red for warnings
    danger: '#D32F2F',
    text: '#121212',
    textDim: '#757575',
    border: '#121212',
    hairline: '#E0E0E0'
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
            <Box sx={{ mb: 4, borderBottom: `1px solid ${THEME.primary}`, pb: 2 }}>
                <Typography variant="h4" sx={{ color: THEME.text, mb: 1, fontFamily: '"Playfair Display", serif', fontWeight: 'bold' }}>
                    Asset Allocation
                </Typography>
                <Typography variant="body1" sx={{ color: THEME.textDim, fontFamily: '"Playfair Display", serif', fontStyle: 'italic' }}>
                    Efficient Frontier Analysis for <span style={{ color: THEME.primary, fontWeight: 'bold', borderBottom: `1px solid ${THEME.success}` }}>{activePortfolio.name}</span>.
                </Typography>
            </Box>

            <Grid container spacing={3} sx={{ height: '100%' }}>
                {/* Left: Chart */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 4, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 0, height: 500, boxShadow: 'none' }}>
                        <Box sx={{ borderBottom: `1px solid ${THEME.hairline}`, mb: 3, pb: 1 }}>
                            <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold' }}>Risk vs Return Profile</Typography>
                        </Box>
                        <ResponsiveContainer width="100%" height="85%">
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke={THEME.hairline} />
                                <XAxis
                                    type="number" dataKey="x" name="Risk (Vol)" unit="%"
                                    stroke={THEME.text} domain={['auto', 'auto']}
                                    label={{ value: 'Risk (Standard Deviation)', position: 'insideBottom', offset: -10, fill: THEME.textDim }}
                                />
                                <YAxis
                                    type="number" dataKey="y" name="Return" unit="%"
                                    stroke={THEME.text} domain={['auto', 'auto']}
                                    label={{ value: 'Expected Return', angle: -90, position: 'insideLeft', fill: THEME.textDim }}
                                />
                                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: THEME.bg, border: `1px solid ${THEME.border}` }} />

                                {/* Simulated Portfolios - Muted Grey/Gold */}
                                <Scatter name="Potential Portfolios" data={frontierData} fill="#BDBDBD" fillOpacity={0.6} shape="circle" />

                                {/* Current Portfolio - Strong Gold Star */}
                                <Scatter name="Current" data={[currentMetrics]} fill={THEME.success} shape="star" z={300} stroke="#000" strokeWidth={1}>
                                    <LabelList dataKey="x" content={() => null} />
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Right: Recommendation */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <Paper sx={{ p: 3, bgcolor: THEME.panel, borderTop: `4px solid ${THEME.success}`, borderRight: `1px solid ${THEME.hairline}`, borderLeft: `1px solid ${THEME.hairline}`, borderBottom: `1px solid ${THEME.hairline}`, borderRadius: 0, boxShadow: 'none' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                <Lightbulb sx={{ color: THEME.success }} />
                                <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 'bold' }}>AI Insight</Typography>
                            </Box>
                            <Typography variant="body1" sx={{ color: THEME.text, mb: 3, lineHeight: 1.6 }}>
                                Your portfolio lies {isOptimal ? 'ON' : 'BELOW'} the efficient frontier.
                            </Typography>

                            {!isOptimal && (
                                <>
                                    <Box sx={{ borderLeft: `3px solid ${THEME.textDim}`, pl: 2, mb: 3 }}>
                                        <Typography variant="body2" sx={{ color: THEME.secondary, fontStyle: 'italic' }}>
                                            "You are taking <b>{(currentMetrics.x).toFixed(1)}%</b> risk for a <b>{(currentMetrics.y).toFixed(1)}%</b> return.
                                            Optimization could boost returns to <b>{(currentMetrics.y * 1.2).toFixed(1)}%</b>."
                                        </Typography>
                                    </Box>
                                    <Chip icon={<AutoGraph />} label="Auto-Optimize Available" sx={{ bgcolor: THEME.text, color: '#fff', borderRadius: 0 }} clickable />
                                </>
                            )}

                            {isOptimal && (
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: THEME.success }}>
                                    <CheckCircle fontSize="small" />
                                    <Typography variant="body2" fontWeight="bold">Portfolio is Efficient</Typography>
                                </Box>
                            )}
                        </Paper>

                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: `1px solid ${THEME.border}`, borderRadius: 0, boxShadow: 'none' }}>
                            <Box sx={{ borderBottom: `1px solid ${THEME.hairline}`, mb: 2, pb: 1 }}>
                                <Typography variant="subtitle2" color={THEME.textDim} sx={{ fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: 1 }}>Current Metrics</Typography>
                            </Box>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="h4" fontWeight="bold" color={THEME.primary}>{currentMetrics.y.toFixed(1)}%</Typography>
                                    <Typography variant="caption" color={THEME.textDim}>Return</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="h4" fontWeight="bold" color={THEME.primary}>{currentMetrics.x.toFixed(1)}%</Typography>
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
