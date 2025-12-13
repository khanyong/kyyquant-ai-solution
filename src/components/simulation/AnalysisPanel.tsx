
import React, { useState } from 'react';
import {
    Box, Paper, Typography, Tabs, Tab, Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow, Grid
} from '@mui/material';
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, BarChart, Bar, Legend
} from 'recharts';
import { BacktestResult } from '../../utils/BacktestEngine';
import { formatLargeNumber } from '../../utils/SimulationEngine';
import { calculateCorrelationMatrix, interpretCorrelation } from '../../utils/CorrelationEngine';

const THEME = {
    bg: '#0B0E14',
    panel: '#151921',
    primary: '#00D1FF', // Cyan
    secondary: '#7F5AF0', // Purple
    text: '#E0E6ED',
    textDim: '#94A1B2',
    border: '#2A2F3A',
    success: '#2CB67D',
    danger: '#EF4565',
    colors: ['#00D1FF', '#7F5AF0', '#FFBB28', '#FF8042', '#2CB67D']
};

export interface NamedResult {
    id: number;
    name: string;
    result: BacktestResult;
    // We need allocations to calculate correlation. 
    // Since BacktestResult doesn't have it, we might need to pass it or mock it.
    // For now, let's assume we can pass allocations via props or extend NamedResult.
    // Actually, AnalysisPanel is usually called with results from PortfolioBacktest. Let's fix types there later. 
    // Valid fix: We will calculate a "Category Correlation" based on just asset names for now if allocations are missing. 
    // UPDATE: I will update the NamedResult interface in the parent or assume we have access to it.
    // BETTER: I'll accept 'allocations' as optional in NamedResult for this feature.
    allocations?: any[];
}

const CorrelationHeatmapView = ({ results }: { results: NamedResult[] }) => {
    // We use the last result (Active Portfolio) as the primary correlation target
    const activeResult = results[results.length - 1];
    const allocations = activeResult?.allocations;

    if (!allocations || allocations.length === 0) {
        return (
            <Box sx={{ p: 4, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
                <Typography variant="h6" color={THEME.text} sx={{ mb: 1 }}>
                    Correlation Data Unavailable
                </Typography>
                <Typography variant="body1" color={THEME.textDim}>
                    Please ensure the portfolio has assets assigned to view the correlation matrix.
                </Typography>
            </Box>
        );
    }

    // Calculate Matrix
    const { assets, matrix } = calculateCorrelationMatrix(allocations);

    return (
        <Box sx={{ p: 1 }}>
            <Box sx={{ overflowX: 'auto', mb: 2 }}>
                <table style={{ borderCollapse: 'separate', borderSpacing: '4px', width: '100%' }}>
                    <thead>
                        <tr>
                            <th style={{ padding: 8 }}></th>
                            {assets.map((asset, i) => (
                                <th key={i} style={{
                                    padding: 8,
                                    color: THEME.textDim,
                                    fontSize: '0.75rem',
                                    fontWeight: 'bold',
                                    writingMode: 'vertical-rl',
                                    transform: 'rotate(180deg)',
                                    height: 100
                                }}>
                                    {asset.length > 15 ? asset.substring(0, 15) + '...' : asset}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {assets.map((rowAsset, i) => (
                            <tr key={i}>
                                <td style={{
                                    padding: 8,
                                    color: THEME.textDim,
                                    fontWeight: 'bold',
                                    fontSize: '0.8rem',
                                    textAlign: 'right',
                                    whiteSpace: 'nowrap'
                                }}>
                                    {rowAsset.length > 20 ? rowAsset.substring(0, 20) + '...' : rowAsset}
                                </td>
                                {matrix[i].map((val, j) => {
                                    // Heatmap Color Logic
                                    let bgColor = 'transparent';
                                    let color = THEME.text;
                                    let opacity = 1;

                                    // Red scale for positive correlation
                                    if (val >= 0) {
                                        // 0 -> 0.05 (transparent), 1 -> 0.8 (red)
                                        const intensity = Math.max(0.05, val * 0.8);
                                        bgColor = `rgba(239, 69, 101, ${intensity})`; // #EF4565
                                    } else {
                                        // Green scale for negative correlation
                                        const intensity = Math.max(0.05, Math.abs(val) * 0.8);
                                        bgColor = `rgba(44, 182, 125, ${intensity})`; // #2CB67D
                                    }

                                    // Highlight self-correlation (diagonal)
                                    if (i === j) {
                                        bgColor = 'rgba(255,255,255,0.05)';
                                        color = THEME.textDim;
                                    }

                                    return (
                                        <td key={j} style={{
                                            padding: '12px 6px',
                                            textAlign: 'center',
                                            backgroundColor: bgColor,
                                            color: color,
                                            borderRadius: 4,
                                            fontSize: '0.85rem'
                                        }}>
                                            {val.toFixed(2)}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </Box>

            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2, display: 'flex', gap: 4 }}>
                <Box>
                    <Typography variant="subtitle2" color={THEME.text} fontWeight="bold" sx={{ mb: 0.5 }}>
                        (Red) High Correlation (&gt; 0.7)
                    </Typography>
                    <Typography variant="caption" color={THEME.textDim}>
                        Assets move together, increasing concentration risk.
                    </Typography>
                </Box>
                <Box>
                    <Typography variant="subtitle2" color={THEME.text} fontWeight="bold" sx={{ mb: 0.5 }}>
                        (Green) Low Correlation (&lt; 0.2)
                    </Typography>
                    <Typography variant="caption" color={THEME.textDim}>
                        Assets move independently, providing diversification.
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
};

// ... existing code ...

interface AnalysisPanelProps {
    results: NamedResult[]; // Array of results for comparison
}

const MetricsTable = ({ results }: { results: NamedResult[] }) => (
    <TableContainer component={Paper} sx={{ bgcolor: 'transparent', boxShadow: 'none', mb: 3 }}>
        <Table size="small">
            <TableHead>
                <TableRow sx={{ '& th': { color: THEME.textDim, borderColor: THEME.border, fontWeight: 'bold' } }}>
                    <TableCell>Metric</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.name}</TableCell>
                    ))}
                </TableRow>
            </TableHead>
            <TableBody>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Initial Balance</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{formatLargeNumber(r.result.initialBalance)}</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Final Balance</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ fontWeight: 'bold' }}>{formatLargeNumber(r.result.finalBalance)}</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>CAGR</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.cagr.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Stdev</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.stdev.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Best Year</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.success }}>{r.result.bestYear.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Worst Year</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.danger }}>{r.result.worstYear.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Max Drawdown</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right" sx={{ color: THEME.danger }}>-{r.result.maxDrawdown.toFixed(2)}%</TableCell>
                    ))}
                </TableRow>
                <TableRow sx={{ '& td': { color: THEME.text, borderColor: THEME.border } }}>
                    <TableCell>Sharpe Ratio</TableCell>
                    {results.map((r) => (
                        <TableCell key={r.id} align="right">{r.result.sharpeRatio.toFixed(2)}</TableCell>
                    ))}
                </TableRow>
            </TableBody>
        </Table>
    </TableContainer>
);

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ results }) => {
    const [tab, setTab] = useState(0);

    // Merge Growth Data for Chart
    // Assuming all simulations have same years/length. 
    // We take the first result's years as X-Axis, and map others.
    const chartData = results.length > 0 ? results[0].result.annualReturns.map((point, idx) => {
        const merged: any = { year: point.year };
        results.forEach(r => {
            if (r.result.annualReturns[idx]) {
                merged[`bal_${r.id}`] = r.result.annualReturns[idx].balance;
                merged[`ret_${r.id}`] = r.result.annualReturns[idx].return;
            }
        });
        return merged;
    }) : [];

    return (
        <Paper sx={{ height: '100%', bgcolor: THEME.panel, border: '1px solid ' + THEME.border, borderRadius: 2, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ borderBottom: 1, borderColor: THEME.border }}>
                <Tabs
                    value={tab}
                    onChange={(_, v) => setTab(v)}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{
                        '& .MuiTab-root': { color: THEME.textDim, minWidth: 100 },
                        '& .Mui-selected': { color: THEME.primary }
                    }}
                >
                    <Tab label="Summary" />
                    <Tab label="Annual Returns" />
                    <Tab label="Metrics" />
                </Tabs>
            </Box>

            <Box sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
                {tab === 0 && (
                    <Box>
                        <MetricsTable results={results} />
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Portfolio Growth</Typography>
                        <Box sx={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <AreaChart data={chartData}>
                                    <defs>
                                        {results.map((r, idx) => (
                                            <linearGradient key={r.id} id={`color${r.id}`} x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor={THEME.colors[idx % THEME.colors.length]} stopOpacity={0.3} />
                                                <stop offset="95%" stopColor={THEME.colors[idx % THEME.colors.length]} stopOpacity={0} />
                                            </linearGradient>
                                        ))}
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis dataKey="year" stroke={THEME.textDim} />
                                    <YAxis stroke={THEME.textDim} tickFormatter={(val) => formatLargeNumber(val)} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                        formatter={(value: number, name: string) => {
                                            return [formatLargeNumber(value), 'Balance']
                                        }}
                                    />
                                    <Legend />
                                    {results.map((r, idx) => (
                                        <Area
                                            key={r.id}
                                            type="monotone"
                                            dataKey={`bal_${r.id}`}
                                            stroke={THEME.colors[idx % THEME.colors.length]}
                                            fill={`url(#color${r.id})`}
                                            name={r.name}
                                            strokeWidth={2}
                                            dot={false}
                                        />
                                    ))}
                                </AreaChart>
                            </ResponsiveContainer>
                        </Box>
                    </Box>
                )}

                {tab === 1 && (
                    <Box>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Annual Returns</Typography>
                        <Box sx={{ height: 400, width: '100%' }}>
                            <ResponsiveContainer>
                                <BarChart data={chartData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                    <XAxis type="number" stroke={THEME.textDim} />
                                    <YAxis dataKey="year" type="category" stroke={THEME.textDim} width={60} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: THEME.bg, border: '1px solid ' + THEME.border }}
                                    />
                                    <Legend />
                                    {results.map((r, idx) => (
                                        <Bar
                                            key={r.id}
                                            dataKey={`ret_${r.id}`}
                                            fill={THEME.colors[idx % THEME.colors.length]}
                                            name={r.name}
                                        />
                                    ))}
                                </BarChart>
                            </ResponsiveContainer>
                        </Box>
                    </Box>
                )}

                {tab === 2 && (
                    <Box>
                        <Box sx={{ mb: 3 }}>
                            {/* Using Metrics Table Here */}
                            <MetricsTable results={results} />
                        </Box>
                    </Box>
                )}

                {tab === 3 && (
                    <CorrelationHeatmapView results={results} />
                )}
            </Box>
        </Paper >
    );
};

export default AnalysisPanel;
