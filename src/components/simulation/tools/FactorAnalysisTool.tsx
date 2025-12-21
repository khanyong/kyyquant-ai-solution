
import React, { useMemo } from 'react';
import {
    Box, Paper, Typography, Grid, Chip
} from '@mui/material';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ResponsiveContainer, Tooltip as RechartsTooltip
} from 'recharts';
import { Portfolio } from '../types';
import { Assessment, Grade, ShowChart } from '@mui/icons-material';

interface FactorAnalysisToolProps {
    activePortfolio: Portfolio;
}

const THEME = {
    bg: 'var(--ipc-bg-primary)',
    panel: 'var(--ipc-bg-panel)',
    primary: 'var(--ipc-primary)',
    secondary: 'var(--ipc-secondary)',
    success: 'var(--ipc-success)',
    warning: 'var(--ipc-warning)',
    danger: 'var(--ipc-danger)',
    text: 'var(--ipc-text-primary)',
    textDim: 'var(--ipc-text-secondary)',
    border: 'var(--ipc-border)'
};

const GRADE_MAP: { [key: string]: number } = {
    'A+': 5.0, 'A': 5.0, 'A-': 4.5,
    'B+': 4.0, 'B': 4.0, 'B-': 3.5,
    'C+': 3.0, 'C': 3.0, 'C-': 2.5,
    'D+': 2.0, 'D': 2.0, 'D-': 1.5,
    'F': 1.0, 'N/A': 3.0 // Neutral fallback
};

const scoreToGrade = (score: number) => {
    if (score >= 4.5) return 'A';
    if (score >= 3.5) return 'B';
    if (score >= 2.5) return 'C';
    if (score >= 1.5) return 'D';
    return 'F';
};

const FactorAnalysisTool: React.FC<FactorAnalysisToolProps> = ({ activePortfolio }) => {

    // Calculate Weighted Factors
    const { chartData, aggregateQuant } = useMemo(() => {
        let totalValuation = 0;
        let totalGrowth = 0;
        let totalProfit = 0;
        let totalMomentum = 0;
        let totalRevisions = 0;
        let totalQuant = 0;
        let totalWeight = 0;

        activePortfolio.allocations.forEach(alloc => {
            const weight = alloc.amount; // Use raw amount as weight
            totalWeight += weight;

            const grades = alloc.asset.factorGrades || {
                valuation: 'C', growth: 'C', profitability: 'C', momentum: 'C', revisions: 'C'
            };

            totalValuation += (GRADE_MAP[grades.valuation] || 3) * weight;
            totalGrowth += (GRADE_MAP[grades.growth] || 3) * weight;
            totalProfit += (GRADE_MAP[grades.profitability] || 3) * weight;
            totalMomentum += (GRADE_MAP[grades.momentum] || 3) * weight;
            totalRevisions += (GRADE_MAP[grades.revisions] || 3) * weight;

            totalQuant += (alloc.asset.quantScore || 3.0) * weight;
        });

        if (totalWeight === 0) return { chartData: [], aggregateQuant: 0 };

        return {
            chartData: [
                { subject: 'Valuation', A: (totalValuation / totalWeight).toFixed(2), fullMark: 5 },
                { subject: 'Growth', A: (totalGrowth / totalWeight).toFixed(2), fullMark: 5 },
                { subject: 'Profitability', A: (totalProfit / totalWeight).toFixed(2), fullMark: 5 },
                { subject: 'Momentum', A: (totalMomentum / totalWeight).toFixed(2), fullMark: 5 },
                { subject: 'EPS Revisions', A: (totalRevisions / totalWeight).toFixed(2), fullMark: 5 },
            ],
            aggregateQuant: totalQuant / totalWeight
        };
    }, [activePortfolio]);

    const quantGrade = scoreToGrade(aggregateQuant);
    const quantColor = quantGrade === 'A' ? THEME.success : quantGrade === 'B' ? THEME.primary : THEME.warning;

    if (activePortfolio.allocations.length === 0) {
        return (
            <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 2 }}>
                <Assessment sx={{ fontSize: 60, color: THEME.textDim }} />
                <Typography variant="h6" color={THEME.textDim}>
                    Add assets to the portfolio to analyze factors.
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3, overflowY: 'auto' }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="bold" sx={{ color: THEME.text, mb: 1 }}>
                    Factor Analysis
                </Typography>
                <Typography variant="body1" sx={{ color: THEME.textDim }}>
                    X-Ray view of <span style={{ color: THEME.primary, fontWeight: 'bold' }}>{activePortfolio.name}</span> across 5 key investment dimensions.
                </Typography>
            </Box>

            <Grid container spacing={3} sx={{ height: '100%' }}>
                {/* Left: Radar Chart */}
                <Grid item xs={12} md={7}>
                    <Paper sx={{ p: 4, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
                                <PolarGrid stroke={THEME.border} />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: THEME.text }} />
                                <PolarRadiusAxis angle={30} domain={[0, 5]} tick={false} axisLine={false} />
                                <Radar
                                    name="Portfolio"
                                    dataKey="A"
                                    stroke={THEME.primary}
                                    strokeWidth={3}
                                    fill={THEME.primary}
                                    fillOpacity={0.3}
                                />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                    itemStyle={{ color: THEME.primary }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Right: Insights */}
                <Grid item xs={12} md={5}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {/* Quant Score Card */}
                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, background: `linear-gradient(135deg, ${THEME.panel} 0%, rgba(0, 209, 255, 0.1) 100%)` }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="h6" fontWeight="bold" color={THEME.text}>Aggregate Quant Score</Typography>
                                <ShowChart sx={{ color: quantColor }} />
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
                                <Typography variant="h3" fontWeight="900" sx={{ color: quantColor }}>
                                    {aggregateQuant.toFixed(2)}
                                </Typography>
                                <Chip label={quantGrade} sx={{ bgcolor: quantColor, color: '#000', fontWeight: 'bold' }} />
                            </Box>
                            <Typography variant="body2" sx={{ mt: 2, color: THEME.textDim }}>
                                Weighted average of proprietary quantitative scores for all holdings. A score above 4.5 indicates "Strong Buy" characteristics.
                            </Typography>
                        </Paper>

                        {/* Factor Details */}
                        <Paper sx={{ p: 3, bgcolor: THEME.panel, border: '1px solid ' + THEME.border, flex: 1 }}>
                            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, color: THEME.text }}>Factor Breakdown</Typography>
                            {chartData?.map((item: any) => (
                                <Box key={item.subject} sx={{ mb: 2 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                        <Typography variant="body2" color={THEME.text}>{item.subject}</Typography>
                                        <Typography variant="body2" fontWeight="bold" color={THEME.primary}>{item.A} / 5.0</Typography>
                                    </Box>
                                    <Box sx={{ height: 6, bgcolor: THEME.bg, borderRadius: 3, overflow: 'hidden' }}>
                                        <Box sx={{ width: `${(item.A / 5) * 100}%`, height: '100%', bgcolor: Number(item.A) > 3.5 ? THEME.success : Number(item.A) > 2.5 ? THEME.warning : THEME.danger }} />
                                    </Box>
                                </Box>
                            ))}
                        </Paper>
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default FactorAnalysisTool;
