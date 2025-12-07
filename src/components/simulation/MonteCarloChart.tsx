import React from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';
import { Paper, Typography, Box, Grid, Chip } from '@mui/material';
import { MonteCarloResult } from '../../utils/SimulationEngine';

interface MonteCarloChartProps {
    data: MonteCarloResult | null;
}

const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ data }) => {
    if (!data || data.years.length === 0) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center', height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">시뮬레이션 데이터가 없습니다.</Typography>
            </Paper>
        );
    }

    // Transform data for Recharts
    const chartData = data.years.map((year, i) => ({
        year,
        p10: Math.round(data.percentiles.p10[i] / 10000), // Man-won unit
        p50: Math.round(data.percentiles.p50[i] / 10000),
        p90: Math.round(data.percentiles.p90[i] / 10000),
        range: [
            Math.round(data.percentiles.p10[i] / 10000),
            Math.round(data.percentiles.p90[i] / 10000)
        ]
    }));

    return (
        <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                    몬테카를로 시뮬레이션 (Portfolio Visualizer)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    자산의 과거 변동성을 기반으로 1,000번의 미래 시나리오를 예측했습니다.
                </Typography>
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center', bgcolor: '#f8f9fa' }}>
                        <Typography variant="caption" color="text.secondary">CAGR (연평균 수익률)</Typography>
                        <Typography variant="h6" fontWeight="bold" color="primary">
                            {data.metrics.cagr.toFixed(2)}%
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={3}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center', bgcolor: '#f8f9fa' }}>
                        <Typography variant="caption" color="text.secondary">Sharpe Ratio (위험대비 효율)</Typography>
                        <Typography variant="h6" fontWeight="bold" color={data.metrics.sharpeRatio > 1 ? 'success.main' : 'text.primary'}>
                            {data.metrics.sharpeRatio.toFixed(2)}
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={3}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center', bgcolor: '#fff0f0' }}>
                        <Typography variant="caption" color="error">Max Drawdown (최대 낙폭)</Typography>
                        <Typography variant="h6" fontWeight="bold" color="error">
                            -{data.metrics.mdd.toFixed(1)}%
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={3}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: 'center', bgcolor: '#f0f7ff' }}>
                        <Typography variant="caption" color="primary">Best Year (최고의 해)</Typography>
                        <Typography variant="h6" fontWeight="bold" color="primary">
                            +{data.metrics.bestYear.toFixed(1)}%
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            <Box sx={{ height: 350, width: '100%' }}>
                <ResponsiveContainer>
                    <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorRange" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#8884d8" stopOpacity={0.05} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="year" />
                        <YAxis
                            unit="만원"
                            tickFormatter={(value) => value >= 10000 ? `${value / 10000}억` : `${value}만`}
                        />
                        <Tooltip
                            formatter={(value: any) => `${value.toLocaleString()} 만원`}
                            labelStyle={{ color: '#666' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="p90"
                            stroke="none"
                            fill="#8884d8"
                            fillOpacity={0.1}
                            name="Optimistic (Top 10%)"
                        />
                        <Area
                            type="monotone"
                            dataKey="p10"
                            stroke="none"
                            fill="#fff" // Clean up bottom
                            fillOpacity={1}
                            name="Pessimistic Base"
                        />
                        <Area
                            type="monotone"
                            dataKey="range"
                            stroke="#8884d8"
                            fill="url(#colorRange)"
                            name="Outcome Range (10-90%)"
                        />
                        <Area
                            type="monotone"
                            dataKey="p50"
                            stroke="#1976d2"
                            strokeWidth={3}
                            fill="none"
                            name="Median Scenario"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </Box>
        </Paper>
    );
};

export default MonteCarloChart;
